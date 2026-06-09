"""
tests/test_mock_dynamic.py
"""
import pytest
from backend.pipeline import run_mock_pipeline

@pytest.mark.anyio
async def test_run_mock_pipeline_dynamic_traces():
    events = []
    def mock_emit(event_name, data):
        events.append((event_name, data))
        
    await run_mock_pipeline(mock_emit)
    
    # Check that document_loaded events are emitted
    assert any(e[0] == "document_loaded" for e in events)
    
    # Check that trace_step events are emitted dynamically
    assert any(e[0] == "trace_step" and e[1]["agent"] == "DocumentAnalyzer" for e in events)
    
    # Check analysis_complete
    complete_events = [e for e in events if e[0] == "analysis_complete"]
    assert len(complete_events) == 1
    assert complete_events[0][1]["is_mock_mode"] is True
