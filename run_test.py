import asyncio
import time
from backend.pipeline import run_analysis_pipeline

async def main():
    start = time.time()
    def emit(event, data):
        print(f"Event: {event}")
    await run_analysis_pipeline(emit)
    print(f"Total time: {time.time() - start:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
