# Technical Debt

## Shortcuts & Assumptions
- **Mock Fallback Override**: Currently relying completely on `run_mock_pipeline` if Azure endpoints fail or are unavailable. We assume the system is being demoed in an environment where Tier 3 fallback provides enough fidelity to demonstrate value.
- **Concurrency Setup**: `ThreadPoolExecutor` is used for document analysis. We assume the number of documents in the `knowledge_base` is relatively small for the hackathon (7 docs). If scaled to 1000s of documents, we would need a proper task queue (e.g., Celery) or an inverted index vector search instead of passing all docs into the pipeline.

## Known Limitations
- The system currently only has two core AI agent capabilities (`DocumentAnalyzer` and `ConflictDetector`). Impact, risk, and resolution downstream agents are mocked.

## Future Improvements
- Implement streaming for intermediate agent reasoning steps.
- Add real RAG (Retrieval-Augmented Generation) layer to prevent LLM context limits when parsing massive documents.

## Codebase Governance (Oversized Files)
- `tests/test_conflict_detector.py`: Currently ~1400 lines. Should be split into smaller test files based on the tested functionality (e.g., `test_schema_validation.py`, `test_pairing_logic.py`, `test_topic_mapping.py`).
- `agents/conflict_detector.py`: Currently ~600 lines. Approaching the upper limit of the governance guidelines. Need to extract helper classes (like `ConflictValidator`, `DuplicateFilter`, `ConfidenceFramework`) into a separate `agents/conflict_helpers.py` utility module.
