"""
tests/test_build_index.py
"""
import sys
from scripts.build_azure_search_index import build_index, main


def test_build_index_dry_run(monkeypatch):
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://example.search.windows.net")
    monkeypatch.setenv("AZURE_SEARCH_KEY", "test-key")
    monkeypatch.setenv("AZURE_SEARCH_INDEX", "rag-test")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

    def mock_embed(texts, *, openrouter_key=None):
        return [[0.1] * 1024 for _ in texts]

    monkeypatch.setattr("scripts.build_azure_search_index.embed_texts", mock_embed)

    metrics = build_index(dry_run=True)

    assert metrics["document_count"] >= 1
    assert metrics["chunk_count"] >= 1
    assert metrics["uploaded"] is False


def test_build_index_cli_dry_run(capsys, monkeypatch):
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://example.search.windows.net")
    monkeypatch.setenv("AZURE_SEARCH_KEY", "test-key")
    monkeypatch.setenv("AZURE_SEARCH_INDEX", "rag-test")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

    def mock_embed(texts, *, openrouter_key=None):
        return [[0.1] * 1024 for _ in texts]

    monkeypatch.setattr("scripts.build_azure_search_index.embed_texts", mock_embed)
    monkeypatch.setattr(sys, "argv", ["build_azure_search_index.py", "--dry-run"])

    main()

    captured = capsys.readouterr()
    assert "Building Azure AI Search index" in captured.out
    assert "Dry run complete" in captured.out
