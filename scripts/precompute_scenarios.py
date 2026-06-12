import asyncio
import json
import os
from agents.orchestrator import ConflictSenseOrchestrator

os.environ["LLM_TIMEOUT_S"] = "15.0"

async def generate_scenario(topic: str, filename: str):
    print(f"Generating scenario for: {topic}")
    orchestrator = ConflictSenseOrchestrator()
    
    events = []
    def emit_fn(event_name, data):
        events.append({"event": event_name, "data": data})
        print(f"  Emitted {event_name}")

    # Override SUPPORTED_TOPICS just for this run to focus on the single topic
    import agents.document_analyzer
    original_topics = agents.document_analyzer.SUPPORTED_TOPICS
    agents.document_analyzer.SUPPORTED_TOPICS = [topic]
    
    import agents.orchestrator
    agents.orchestrator.SUPPORTED_TOPICS = [topic]
    
    try:
        await orchestrator.run_analysis(emit_fn)
        
        os.makedirs("data/precomputed", exist_ok=True)
        with open(f"data/precomputed/{filename}.json", "w") as f:
            json.dump(events, f, indent=2)
        print(f"Saved {filename}.json")
    finally:
        agents.document_analyzer.SUPPORTED_TOPICS = original_topics
        agents.orchestrator.SUPPORTED_TOPICS = original_topics

async def main():
    scenarios = [
        ("cross-border IT policies vs HR flexibility", "scenario_1_data_residency"),
        ("whistleblower protection vs IT identity logging", "scenario_2_anonymous_reporting"),
        ("VPN access vs export control rules", "scenario_3_cross_border"),
        ("third-party software SLAs vs internal security audits", "scenario_4_vendor_compliance"),
        ("whistleblower reporting anonymity and IT security logging rules", "scenario_5_nexora_demo"),
    ]
    for topic, filename in scenarios:
        try:
            await generate_scenario(topic, filename)
        except Exception as e:
            print(f"Failed {filename}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
