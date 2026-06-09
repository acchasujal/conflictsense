import pytest
from unittest.mock import MagicMock
from agents.azure_search_retriever import AzureSearchRetriever

def test_azure_search_successful_retrieval(monkeypatch):
    retriever = AzureSearchRetriever()
    retriever._available = True
    
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "value": [
            {
                "chunk_id": "1",
                "title": "doc1.md",
                "parent_id": "§1.1",
                "chunk": "test content",
                "@search.score": 0.9
            }
        ]
    }
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client_instance
    
    monkeypatch.setattr("httpx.Client", lambda timeout: mock_client)
    
    chunks = retriever.search("query")
    assert len(chunks) == 1
    assert chunks[0].id == "1"
    assert chunks[0].document_name == "doc1.md"
    assert chunks[0].section_id == "§1.1"

def test_azure_search_zero_results(monkeypatch):
    retriever = AzureSearchRetriever()
    retriever._available = True
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"value": []}
    
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client_instance
    
    monkeypatch.setattr("httpx.Client", lambda timeout: mock_client)
    
    with pytest.raises(RuntimeError, match="zero results"):
        retriever.search("query")

def test_azure_search_auth_failure(monkeypatch):
    retriever = AzureSearchRetriever()
    retriever._available = True
    
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("403 Forbidden")
    
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client_instance
    
    monkeypatch.setattr("httpx.Client", lambda timeout: mock_client)
    
    with pytest.raises(RuntimeError, match="request failed"):
        retriever.search("query")

def test_azure_search_not_available():
    retriever = AzureSearchRetriever()
    retriever._available = False
    
    with pytest.raises(RuntimeError, match="not configured"):
        retriever.search("query")
