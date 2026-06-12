import asyncio
import logging
import time
from agents.llm_provider import get_provider_chain
from agents.document_analyzer import DocumentAnalyzer
from agents.conflict_detector import _SYSTEM_PROMPT, _USER_PROMPT_TEMPLATE

logging.basicConfig(level=logging.INFO)

async def audit():
    chain = get_provider_chain()
    print("Provider Chain Audit")
    print("=" * 40)
    
    # We'll simulate a conflict detection call
    topic = "employee data location and processing rules"
    block = "Mock statement block for benchmarking."
    user_prompt = _USER_PROMPT_TEMPLATE.format(topic=topic, statements_block=block)
    
    for provider in chain.providers:
        print(f"\nBenchmarking Provider: {provider.name}")
        successes = 0
        latencies = []
        for i in range(3):
            t0 = time.monotonic()
            try:
                # Force specific provider by temporarily modifying the chain list
                original_providers = chain.providers
                chain.providers = [provider]
                data, resp = chain.complete_json(
                    _SYSTEM_PROMPT, user_prompt, mock_factory=lambda: {}, allow_mock=False
                )
                duration = time.monotonic() - t0
                successes += 1
                latencies.append(duration)
                print(f"  Run {i+1}: Success in {duration:.2f}s")
            except Exception as e:
                duration = time.monotonic() - t0
                print(f"  Run {i+1}: Failed in {duration:.2f}s ({e})")
            finally:
                chain.providers = original_providers
        
        if successes > 0:
            avg_latency = sum(latencies) / successes
            print(f"Result: {successes}/3 successful. Avg latency: {avg_latency:.2f}s")
        else:
            print(f"Result: 0/3 successful.")

if __name__ == "__main__":
    asyncio.run(audit())
