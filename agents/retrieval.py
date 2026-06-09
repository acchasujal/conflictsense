"""
agents/retrieval.py

Lightweight local retrieval layer for DocumentAnalyzer.
Chunks markdown files, embeds them using Gemini, and performs cosine similarity search.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("conflictsense.retrieval")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


@dataclass
class Chunk:
    id: str
    document_name: str
    section_id: str
    text: str
    embedding: Optional[list[float]] = None


class LocalRetriever:
    """
    Lightweight in-memory retriever for policy documents with persistence.
    """

    INDEX_PATH = Path(__file__).parent.parent / "data" / "retrieval_index.json"

    def __init__(self, kb_dir: Path | str | None = None) -> None:
        if kb_dir is None:
            self.kb_dir = Path(__file__).parent.parent / "knowledge_base"
        else:
            self.kb_dir = Path(kb_dir)
            
        self.chunks: list[Chunk] = []
        self._available = bool(GEMINI_API_KEY)
        
        # Metrics
        self.chunk_count = 0
        self.document_count = 0
        self.last_retrieval_latency = 0.0
        self.top_k_used = 0
        
        self._load_and_chunk()
        
        if not self._available:
            logger.warning("LocalRetriever: GEMINI_API_KEY not set. Retrieval will fall back to returning first few chunks.")

    def _get_file_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _load_index(self) -> tuple[list[Chunk], dict[str, str]]:
        if not self.INDEX_PATH.exists():
            return [], {}
        try:
            with open(self.INDEX_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            chunks = [Chunk(**c) for c in data.get("chunks", [])]
            hashes = data.get("hashes", {})
            return chunks, hashes
        except Exception as e:
            logger.error("Failed to load retrieval index: %s", e)
            return [], {}

    def _save_index(self, hashes: dict[str, str]) -> None:
        self.INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "hashes": hashes,
            "chunks": [asdict(c) for c in self.chunks]
        }
        with open(self.INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _load_and_chunk(self) -> None:
        if not self.kb_dir.exists():
            logger.error("knowledge_base/ directory not found at %s", self.kb_dir)
            return

        existing_chunks, existing_hashes = self._load_index()
        new_chunks = []
        new_hashes = {}
        
        docs_processed = 0
        docs_rebuilt = 0
        
        for path in sorted(self.kb_dir.glob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
                file_hash = self._get_file_hash(text)
                new_hashes[path.name] = file_hash
                docs_processed += 1
                
                if path.name in existing_hashes and existing_hashes[path.name] == file_hash:
                    # File unchanged, load existing chunks
                    doc_chunks = [c for c in existing_chunks if c.document_name == path.name]
                    self.chunks.extend(doc_chunks)
                else:
                    # File changed or new, re-chunk
                    docs_rebuilt += 1
                    doc_chunks = self._chunk_markdown(path.name, text)
                    new_chunks.extend(doc_chunks)
                    self.chunks.extend(doc_chunks)
                    logger.debug("Chunked %s into %d chunks", path.name, len(doc_chunks))
            except OSError as e:
                logger.error("Failed to load %s: %s", path.name, e)
                
        if new_chunks and self._available:
            self._embed_chunks(new_chunks)
            self._save_index(new_hashes)
        elif new_chunks and not self._available:
            # We still want to save index for chunks without embeddings so we don't rechunk them next time
            self._save_index(new_hashes)
            
        self.chunk_count = len(self.chunks)
        self.document_count = docs_processed
        logger.info("LocalRetriever: Loaded %d chunks from %d docs (Rebuilt %d)", self.chunk_count, self.document_count, docs_rebuilt)

    @staticmethod
    def _chunk_markdown(doc_name: str, text: str) -> list[Chunk]:
        """
        Splits markdown text into chunks based on headers (## or ###).
        """
        chunks = []
        # Split by ## or ### but keep the delimiter
        parts = re.split(r'(?m)^(?=#{2,3} )', text)
        
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
                
            # Extract section ID like §4.2 or default to chunk index
            sec_match = re.search(r'(§\d+(?:\.\d+)?)', part)
            section_id = sec_match.group(1) if sec_match else f"chunk-{i}"
            
            chunk_id = f"{doc_name}::{section_id}::{i}"
            chunks.append(Chunk(
                id=chunk_id,
                document_name=doc_name,
                section_id=section_id,
                text=part
            ))
            
        return chunks

    def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Fetch embeddings from Gemini API in batches."""
        if not GEMINI_API_KEY:
            return []
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents?key={GEMINI_API_KEY}"
        
        requests = []
        for t in texts:
            requests.append({
                "model": "models/text-embedding-004",
                "content": {"parts": [{"text": t}]}
            })
            
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json={"requests": requests})
                response.raise_for_status()
                data = response.json()
                
            embeddings = []
            for item in data.get("embeddings", []):
                embeddings.append(item.get("values", []))
            return embeddings
        except Exception as e:
            logger.error("Failed to fetch embeddings: %s", e)
            return []

    def _embed_chunks(self, chunks_to_embed: list[Chunk]) -> None:
        """Embed a specific list of chunks."""
        t0 = time.monotonic()
        texts = [c.text for c in chunks_to_embed]
        if not texts:
            return
            
        # Batch size for Gemini API is usually around 100
        embeddings = self._get_embeddings(texts)
        if len(embeddings) == len(chunks_to_embed):
            for i, chunk in enumerate(chunks_to_embed):
                chunk.embedding = embeddings[i]
            logger.info("LocalRetriever: Embedded %d new chunks in %.2fs", len(chunks_to_embed), time.monotonic() - t0)
        else:
            logger.error("LocalRetriever: Embedding count mismatch (got %d, expected %d)", len(embeddings), len(chunks_to_embed))

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def search(self, query: str, top_k: int = 5) -> list[Chunk]:
        """
        Retrieve the top_k most relevant chunks across all documents.
        """
        t0 = time.monotonic()
        self.top_k_used = top_k
        
        if not self._available or not self.chunks or not self.chunks[0].embedding:
            # Fallback if no embeddings: just return first few chunks
            self.last_retrieval_latency = time.monotonic() - t0
            return self.chunks[:top_k]
            
        # Embed the query
        query_emb_list = self._get_embeddings([query])
        if not query_emb_list:
            self.last_retrieval_latency = time.monotonic() - t0
            return self.chunks[:top_k]
            
        query_emb = query_emb_list[0]
        
        # Calculate similarities
        scored_chunks = []
        for chunk in self.chunks:
            if chunk.embedding:
                score = self._cosine_similarity(query_emb, chunk.embedding)
                scored_chunks.append((score, chunk))
                
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        result = [chunk for score, chunk in scored_chunks[:top_k]]
        self.last_retrieval_latency = time.monotonic() - t0
        return result

    def retrieve_for_document(self, query: str, doc_name: str, top_k: int = 3) -> list[Chunk]:
        """
        Retrieve the top_k most relevant chunks for a specific document.
        """
        t0 = time.monotonic()
        self.top_k_used = top_k
        
        doc_chunks = [c for c in self.chunks if c.document_name == doc_name]
        
        if not self._available or not doc_chunks or not doc_chunks[0].embedding:
            # Fallback if no embeddings: just return first few chunks
            self.last_retrieval_latency = time.monotonic() - t0
            return doc_chunks[:top_k]
            
        # Embed the query
        query_emb_list = self._get_embeddings([query])
        if not query_emb_list:
            self.last_retrieval_latency = time.monotonic() - t0
            return doc_chunks[:top_k]
            
        query_emb = query_emb_list[0]
        
        # Calculate similarities
        scored_chunks = []
        for chunk in doc_chunks:
            if chunk.embedding:
                score = self._cosine_similarity(query_emb, chunk.embedding)
                scored_chunks.append((score, chunk))
                
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        result = [chunk for score, chunk in scored_chunks[:top_k]]
        self.last_retrieval_latency = time.monotonic() - t0
        return result

    def get_metrics(self) -> dict:
        return {
            "chunk_count": self.chunk_count,
            "document_count": self.document_count,
            "last_retrieval_latency_s": round(self.last_retrieval_latency, 4),
            "top_k_used": self.top_k_used,
        }
