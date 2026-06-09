"""
agents/azure_search_retriever.py

Connects to Azure AI Search to retrieve document chunks.
Uses REST API to perform retrieval.
"""

from __future__ import annotations

import logging
import os
import httpx
from typing import Optional
from dotenv import load_dotenv

from agents.retrieval import Chunk

load_dotenv()
logger = logging.getLogger("conflictsense.azure_search")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY", "")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "rag-1781022790838")
API_VERSION = os.getenv("AZURE_SEARCH_API_VERSION", "2023-11-01")


class AzureSearchRetriever:
    """
    Retrieves document chunks from Azure AI Search using REST API.
    """
    def __init__(self):
        self._available = bool(AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY and AZURE_SEARCH_INDEX)
        if not self._available:
            logger.warning("AzureSearchRetriever: Missing Azure Search credentials. Will fallback.")

    def search(self, query: str, top_k: int = 5) -> list[Chunk]:
        """
        Query Azure AI Search for the top_k most relevant chunks across all documents.
        """
        if not self._available:
            raise RuntimeError("Azure Search credentials not configured")

        url = f"{AZURE_SEARCH_ENDPOINT.rstrip('/')}/indexes/{AZURE_SEARCH_INDEX}/docs/search?api-version={API_VERSION}"
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_SEARCH_KEY
        }
        
        payload = {
            "search": query,
            "top": top_k,
            "searchFields": "chunk,title",
            "queryType": "semantic",
            "semanticConfiguration": "rag-1781022790838-semantic-configuration"
        }
        
        # Get query embedding
        if OPENROUTER_API_KEY:
            try:
                emb_url = "https://openrouter.ai/api/v1/embeddings"
                emb_headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }
                emb_payload = {
                    "model": "openai/text-embedding-3-small",
                    "input": query,
                    "dimensions": 1024
                }
                with httpx.Client() as client:
                    emb_res = client.post(emb_url, headers=emb_headers, json=emb_payload, timeout=10.0)
                    emb_res.raise_for_status()
                    emb_data = emb_res.json()
                    query_vector = emb_data['data'][0]['embedding']
                    
                payload["vectorQueries"] = [
                    {
                        "kind": "vector",
                        "vector": query_vector,
                        "exhaustive": True,
                        "fields": "text_vector",
                        "k": top_k
                    }
                ]
            except Exception as e:
                logger.warning("Failed to get query embedding, falling back to pure semantic search: %s", e)

        try:
            import time
            t0 = time.monotonic()
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            self.last_latency = int((time.monotonic() - t0) * 1000)
        except Exception as e:
            logger.error("Azure AI Search request failed: %s", e)
            self.last_latency = 0
            raise RuntimeError(f"Azure Search request failed: {e}") from e

        chunks = []
        for item in data.get("value", []):
            c_id = item.get("chunk_id", "unknown_id")
            doc_name = item.get("title", "unknown_doc.md")
            section_id = item.get("parent_id", "unknown_section")
            text = item.get("chunk", "")
            score = item.get("@search.score", 0.0)
            
            chunk = Chunk(
                id=str(c_id),
                document_name=str(doc_name),
                section_id=str(section_id),
                text=str(text),
                embedding=None
            )
            # Store the score in the Chunk dynamically (if python allows extending dataclass, or we can just append it).
            # We will patch it temporarily.
            setattr(chunk, "retrieval_score", score)
            chunks.append(chunk)

        if not chunks:
            # Task 4 specifies "If Azure Search returns zero results automatically switch to LocalRetriever."
            # Raising an exception will trigger the except block in DocumentAnalyzer
            raise RuntimeError("Azure Search returned zero results")

        return chunks
