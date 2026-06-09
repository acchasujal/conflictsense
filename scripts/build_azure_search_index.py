#!/usr/bin/env python3
"""
scripts/build_azure_search_index.py

Build the Azure AI Search index from the ConflictSense knowledge base.

Pipeline:
  knowledge_base/*.md
    -> markdown chunking (section-aware splits)
    -> embedding generation (OpenRouter text-embedding-3-small, 1024-dim)
    -> Azure AI Search mergeOrUpload

Prerequisites (.env):
  AZURE_SEARCH_ENDPOINT
  AZURE_SEARCH_KEY
  AZURE_SEARCH_INDEX          (default: rag-1781022790838)
  OPENROUTER_API_KEY          (required for 1024-dim vectors matching the index)

Usage:
  python scripts/build_azure_search_index.py
  python scripts/build_azure_search_index.py --dry-run
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from agents.retrieval import LocalRetriever, Chunk

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("conflictsense.build_index")

EMBEDDING_MODEL = "openai/text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1024
EMBED_BATCH_SIZE = 32


def _search_config() -> dict[str, str]:
    return {
        "endpoint": os.getenv("AZURE_SEARCH_ENDPOINT", ""),
        "key": os.getenv("AZURE_SEARCH_KEY", ""),
        "index": os.getenv("AZURE_SEARCH_INDEX", "rag-1781022790838"),
        "api_version": os.getenv("AZURE_SEARCH_API_VERSION", "2023-11-01"),
        "openrouter_key": os.getenv("OPENROUTER_API_KEY", ""),
    }


def _require_config() -> dict[str, str]:
    cfg = _search_config()
    missing = [
        name
        for name, value in (
            ("AZURE_SEARCH_ENDPOINT", cfg["endpoint"]),
            ("AZURE_SEARCH_KEY", cfg["key"]),
            ("AZURE_SEARCH_INDEX", cfg["index"]),
            ("OPENROUTER_API_KEY", cfg["openrouter_key"]),
        )
        if not value
    ]
    if missing:
        raise SystemExit(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Set them in .env before indexing."
        )
    return cfg


def load_chunks(kb_dir: Path | None = None) -> list[Chunk]:
    """Chunk all markdown files in knowledge_base/."""
    kb_path = kb_dir or (root_dir / "knowledge_base")
    if not kb_path.exists():
        raise SystemExit(f"knowledge_base/ not found at {kb_path}")

    chunks: list[Chunk] = []
    for path in sorted(kb_path.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        doc_chunks = LocalRetriever._chunk_markdown(path.name, text)
        chunks.extend(doc_chunks)
        logger.info("Chunked %s into %d sections", path.name, len(doc_chunks))

    if not chunks:
        raise SystemExit("No markdown documents found in knowledge_base/")

    return chunks


def embed_texts(texts: list[str], *, openrouter_key: str | None = None) -> list[list[float]]:
    """Generate 1024-dim embeddings via OpenRouter (matches Azure index schema)."""
    api_key = openrouter_key or os.getenv("OPENROUTER_API_KEY", "")
    url = "https://openrouter.ai/api/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    embeddings: list[list[float]] = []
    with httpx.Client(timeout=60.0) as client:
        for start in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[start : start + EMBED_BATCH_SIZE]
            payload = {
                "model": EMBEDDING_MODEL,
                "input": batch,
                "dimensions": EMBEDDING_DIMENSIONS,
            }
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            batch_embeddings = [item["embedding"] for item in data.get("data", [])]
            if len(batch_embeddings) != len(batch):
                raise RuntimeError(
                    f"Embedding count mismatch: expected {len(batch)}, got {len(batch_embeddings)}"
                )
            embeddings.extend(batch_embeddings)

    return embeddings


def to_search_documents(chunks: list[Chunk], embeddings: list[list[float]]) -> list[dict]:
    """Map Chunk objects to Azure AI Search document schema."""
    documents = []
    for chunk, vector in zip(chunks, embeddings):
        documents.append(
            {
                "@search.action": "mergeOrUpload",
                "chunk_id": chunk.id,
                "parent_id": chunk.section_id,
                "title": chunk.document_name,
                "chunk": chunk.text,
                "text_vector": vector,
            }
        )
    return documents


def upload_documents(documents: list[dict], cfg: dict[str, str]) -> dict:
    """Upload documents to Azure AI Search."""
    url = (
        f"{cfg['endpoint'].rstrip('/')}/indexes/{cfg['index']}"
        f"/docs/index?api-version={cfg['api_version']}"
    )
    headers = {
        "Content-Type": "application/json",
        "api-key": cfg["key"],
    }
    payload = {"value": documents}

    with httpx.Client(timeout=120.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()


def build_index(*, kb_dir: Path | None = None, dry_run: bool = False) -> dict:
    """Run the full knowledge_base -> Azure AI Search indexing pipeline."""
    cfg = _require_config()

    chunks = load_chunks(kb_dir)
    doc_names = sorted({chunk.document_name for chunk in chunks})
    logger.info("Loaded %d chunks from %d documents", len(chunks), len(doc_names))

    texts = [chunk.text for chunk in chunks]
    embeddings = embed_texts(texts, openrouter_key=cfg["openrouter_key"])
    documents = to_search_documents(chunks, embeddings)

    if dry_run:
        logger.info("Dry run: prepared %d documents (no upload)", len(documents))
        return {
            "document_count": len(doc_names),
            "chunk_count": len(chunks),
            "uploaded": False,
        }

    result = upload_documents(documents, cfg)
    failed = [item for item in result.get("value", []) if not item.get("status")]
    if failed:
        raise RuntimeError(f"Azure AI Search upload failed for {len(failed)} documents")

    logger.info("Indexed %d chunks into Azure AI Search index '%s'", len(documents), cfg["index"])
    return {
        "document_count": len(doc_names),
        "chunk_count": len(chunks),
        "uploaded": True,
        "index": cfg["index"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index knowledge_base documents into Azure AI Search."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chunk and embed only; do not upload to Azure AI Search.",
    )
    args = parser.parse_args()

    print("Building Azure AI Search index...")
    print("  knowledge_base -> chunking -> embeddings -> Azure AI Search")

    metrics = build_index(dry_run=args.dry_run)

    print(f"\nDocuments processed: {metrics['document_count']}")
    print(f"Chunks generated: {metrics['chunk_count']}")
    if metrics.get("uploaded"):
        print(f"Index: {metrics['index']}")
        print("\nAzure AI Search index built successfully.")
    else:
        print("\nDry run complete (no upload).")


if __name__ == "__main__":
    main()
