"""
tests/test_retrieval.py

Tests for the new LocalRetriever grounding layer.
"""

from agents.retrieval import LocalRetriever, Chunk


def test_chunk_markdown():
    markdown = """# Title
    
## §1.1
This is section 1.1

## §1.2
This is section 1.2
"""
    chunks = LocalRetriever._chunk_markdown("test.md", markdown)
    assert len(chunks) == 3
    assert chunks[0].section_id == "chunk-0"
    assert chunks[1].section_id == "§1.1"
    assert "This is section 1.1" in chunks[1].text
    assert chunks[2].section_id == "§1.2"
    assert "This is section 1.2" in chunks[2].text


def test_cosine_similarity():
    retriever = LocalRetriever(kb_dir="dummy")
    
    a = [1.0, 0.0, 0.0]
    b = [1.0, 0.0, 0.0]
    assert retriever._cosine_similarity(a, b) == 1.0
    
    c = [0.0, 1.0, 0.0]
    assert retriever._cosine_similarity(a, c) == 0.0


def test_retrieve_for_document_fallback():
    # If no embeddings are available, should return first k chunks
    retriever = LocalRetriever(kb_dir="dummy")
    retriever._available = False
    
    # Manually add some chunks
    retriever.chunks = [
        Chunk(id="1", document_name="doc1", section_id="s1", text="text1"),
        Chunk(id="2", document_name="doc1", section_id="s2", text="text2"),
        Chunk(id="3", document_name="doc2", section_id="s1", text="text3"),
    ]
    
    results = retriever.retrieve_for_document("query", "doc1", top_k=1)
    assert len(results) == 1
    assert results[0].id == "1"


def test_retrieve_for_document_ranking(monkeypatch):
    retriever = LocalRetriever(kb_dir="dummy")
    retriever._available = True
    
    # Mock embeddings so that query matches "best"
    def mock_get_embeddings(texts):
        embs = []
        for t in texts:
            if "query" in t:
                embs.append([1.0, 0.0])
            elif "best text" in t:
                embs.append([0.9, 0.1])
            elif "worst text" in t:
                embs.append([0.1, 0.9])
            else:
                embs.append([0.5, 0.5])
        return embs
        
    monkeypatch.setattr(retriever, "_get_embeddings", mock_get_embeddings)
    
    retriever.chunks = [
        Chunk(id="1", document_name="doc1", section_id="s1", text="worst text", embedding=[0.1, 0.9]),
        Chunk(id="2", document_name="doc1", section_id="s2", text="best text", embedding=[0.9, 0.1]),
        Chunk(id="3", document_name="doc1", section_id="s3", text="mid text", embedding=[0.5, 0.5]),
    ]
    
    results = retriever.retrieve_for_document("query", "doc1", top_k=2)
    assert len(results) == 2
    assert results[0].id == "2" # best match
    assert results[1].id == "3" # mid match


def test_document_analyzer_uses_chunks(monkeypatch):
    from agents.document_analyzer import DocumentAnalyzer
    from unittest.mock import MagicMock
    
    # Create mock retriever that returns a specific chunk
    class MockRetriever:
        def retrieve_for_document(self, query, doc_name, top_k):
            return [Chunk(id="1", document_name=doc_name, section_id="s1", text="MOCK_CHUNK_TEXT")]
            
    analyzer = DocumentAnalyzer(foundry_client=MagicMock())
    analyzer._retriever = MockRetriever()
    analyzer._documents = {"doc1.md": "FULL_DOC_TEXT_THAT_SHOULD_BE_IGNORED"}
    
    # Intercept query_document to check what document_text was passed
    passed_text = []
    def mock_query_doc(query, document_name, document_text, topic, require_grounded_citations):
        passed_text.append(document_text)
        from agents.foundry_iq_client import _mock_result
        return _mock_result(document_name, topic, query)
        
    analyzer._client.query_document.side_effect = mock_query_doc
    
    analyzer.analyze_single_document("topic", "doc1.md")
    
    assert len(passed_text) == 1
    assert "MOCK_CHUNK_TEXT" in passed_text[0]
    assert "FULL_DOC_TEXT_THAT_SHOULD_BE_IGNORED" not in passed_text[0]
