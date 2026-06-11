#!/usr/bin/env python3
"""
scripts/measure_providers.py
Measures latency, stability, and rate-limiting behavior of all configured LLM providers.
"""

import os
import sys
import time
import json
import logging
import asyncio
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path to import agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.llm_provider import (
    GeminiProvider,
    OpenRouterProvider,
    GroqProvider,
    NvidiaProvider,
    LLMProvider,
    LLMResponse
)

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("provider_measurement")

SYSTEM_PROMPT = """You are a Conflict Validator. You review proposed policy conflicts.
Determine if the conflict is a genuine structural impossibility.
Return JSON with structure: {"status": "REJECTED", "reasoning": "some reasoning", "confidence": 95}"""

USER_PROMPT = """Title: Vacation Policy Mismatch
Reasoning: Policy A says 20 days vacation, Policy B says 25 days annual leave.
Citations:
- [doc1.txt Sec 1] Employees get 20 days vacation per year.
- [doc2.txt Sec 2] Employees get 25 days annual leave per year."""


def run_single_request(provider: LLMProvider, i: int) -> Dict[str, Any]:
    """Runs a single request and measures results."""
    t0 = time.monotonic()
    try:
        response = provider.complete(SYSTEM_PROMPT, USER_PROMPT, json_mode=True)
        elapsed = time.monotonic() - t0
        # Validate that JSON parsing succeeds
        data = json.loads(response.content)
        return {
            "success": True,
            "latency": elapsed,
            "error": None,
            "content_len": len(response.content),
            "provider_reported_elapsed": response.elapsed_s,
            "parsed_status": data.get("status")
        }
    except Exception as e:
        elapsed = time.monotonic() - t0
        return {
            "success": False,
            "latency": elapsed,
            "error": f"{type(e).__name__}: {str(e)}",
            "content_len": 0,
            "provider_reported_elapsed": 0.0,
            "parsed_status": None
        }


def run_sequential_benchmark(provider: LLMProvider, count: int = 10) -> List[Dict[str, Any]]:
    """Runs sequential requests to measure latency under normal conditions."""
    results = []
    print(f"Running {count} sequential requests for provider '{provider.name}'...")
    for i in range(count):
        print(f"  Request {i+1}/{count}...", end="", flush=True)
        res = run_single_request(provider, i)
        results.append(res)
        if res["success"]:
            print(f" Success in {res['latency']:.2f}s")
        else:
            print(f" FAILED: {res['error']}")
        # Brief sleep to avoid hitting immediate rate limits during sequential testing
        time.sleep(0.5)
    return results


def run_concurrent_benchmark(provider: LLMProvider, count: int = 5) -> List[Dict[str, Any]]:
    """Runs concurrent requests to test rate limiting / stability under load."""
    print(f"Running {count} concurrent requests for provider '{provider.name}'...")
    results = [None] * count
    
    with ThreadPoolExecutor(max_workers=count) as executor:
        futures = {
            executor.submit(run_single_request, provider, i): i 
            for i in range(count)
        }
        for future in futures:
            i = futures[future]
            try:
                results[i] = future.result()
            except Exception as e:
                results[i] = {
                    "success": False,
                    "latency": 0.0,
                    "error": f"ExecutorException: {str(e)}",
                    "content_len": 0,
                    "provider_reported_elapsed": 0.0,
                    "parsed_status": None
                }
                
    for i, res in enumerate(results):
        status = "Success" if res["success"] else "FAILED"
        print(f"  Concurrent {i+1}: {status} in {res['latency']:.2f}s (Error: {res['error']})")
        
    return results


def analyze_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]
    
    success_rate = (len(successes) / len(results)) * 100 if results else 0.0
    latencies = [r["latency"] for r in successes]
    
    if latencies:
        avg_lat = sum(latencies) / len(latencies)
        min_lat = min(latencies)
        max_lat = max(latencies)
        sorted_lat = sorted(latencies)
        median_lat = sorted_lat[len(sorted_lat) // 2]
    else:
        avg_lat = min_lat = max_lat = median_lat = 0.0
        
    errors = {}
    for r in failures:
        err = r["error"] or "Unknown Error"
        # Truncate long error messages
        if len(err) > 80:
            err = err[:80] + "..."
        errors[err] = errors.get(err, 0) + 1
        
    return {
        "success_rate": success_rate,
        "avg_latency": avg_lat,
        "median_latency": median_lat,
        "min_latency": min_lat,
        "max_latency": max_lat,
        "total_requests": len(results),
        "success_count": len(successes),
        "failure_count": len(failures),
        "errors": errors
    }


def main():
    # Make sure we don't skip live providers (remove PYTEST_CURRENT_TEST just in case)
    if "PYTEST_CURRENT_TEST" in os.environ:
        del os.environ["PYTEST_CURRENT_TEST"]

    providers = [
        GeminiProvider(),
        OpenRouterProvider(),
        GroqProvider(),
        NvidiaProvider()
    ]
    
    summary = {}
    
    for p in providers:
        print("\n" + "="*50)
        print(f"BENCHMARKING PROVIDER: {p.name.upper()} ({p.model})")
        print("="*50)
        
        if not p.available:
            print(f"Provider {p.name} is NOT configured (API key missing). Skipping.")
            continue
            
        # 1. Sequential Benchmark (8 requests)
        seq_results = run_sequential_benchmark(p, count=8)
        seq_stats = analyze_results(seq_results)
        
        # 2. Concurrent Benchmark (5 requests)
        con_results = run_concurrent_benchmark(p, count=5)
        con_stats = analyze_results(con_results)
        
        # Combine
        combined_results = seq_results + con_results
        combined_stats = analyze_results(combined_results)
        
        summary[p.name] = {
            "model": p.model,
            "seq": seq_stats,
            "con": con_stats,
            "combined": combined_stats
        }
        
        print("\nResults for", p.name.upper())
        print(f"  Sequential Success Rate: {seq_stats['success_rate']:.1f}% | Avg Latency: {seq_stats['avg_latency']:.2f}s")
        print(f"  Concurrent Success Rate: {con_stats['success_rate']:.1f}% | Avg Latency: {con_stats['avg_latency']:.2f}s")
        if combined_stats["errors"]:
            print("  Errors encountered:")
            for err, count in combined_stats["errors"].items():
                print(f"    - [{count}x] {err}")
                
    # Write report to markdown file
    report_path = "docs/provider_benchmark_report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Provider Benchmark Results\n\n")
        f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Overview of Provider Metrics\n\n")
        f.write("| Provider | Model | Seq Success | Seq Avg Latency | Con Success | Con Avg Latency | Combined Success | Errors |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")
        for name, data in summary.items():
            err_str = ", ".join(f"{err} ({cnt}x)" for err, cnt in data["combined"]["errors"].items()) or "None"
            f.write(f"| {name} | `{data['model']}` | {data['seq']['success_rate']:.1f}% ({data['seq']['success_count']}/{data['seq']['total_requests']}) | {data['seq']['avg_latency']:.2f}s | {data['con']['success_rate']:.1f}% ({data['con']['success_count']}/{data['con']['total_requests']}) | {data['con']['avg_latency']:.2f}s | {data['combined']['success_rate']:.1f}% | {err_str} |\n")
        
        f.write("\n## Latency Statistics (Combined Seq + Con)\n\n")
        f.write("| Provider | Min Latency | Median Latency | Max Latency | Avg Latency |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for name, data in summary.items():
            f.write(f"| {name} | {data['combined']['min_latency']:.2f}s | {data['combined']['median_latency']:.2f}s | {data['combined']['max_latency']:.2f}s | {data['combined']['avg_latency']:.2f}s |\n")
            
        f.write("\n## Detailed Analysis and Verdicts\n\n")
        
        # Compute recommendation
        recommendations = []
        # Fastest
        sorted_by_latency = sorted([(n, d["combined"]["avg_latency"]) for n, d in summary.items() if d["combined"]["success_count"] > 0], key=lambda x: x[1])
        if sorted_by_latency:
            f.write(f"- **Fastest Provider**: {sorted_by_latency[0][0]} (Avg {sorted_by_latency[0][1]:.2f}s)\n")
        
        # Most Stable (Success Rate)
        sorted_by_stability = sorted([(n, d["combined"]["success_rate"]) for n, d in summary.items()], key=lambda x: x[1], reverse=True)
        if sorted_by_stability:
            f.write(f"- **Most Stable Provider**: {sorted_by_stability[0][0]} ({sorted_by_stability[0][1]:.1f}% success rate)\n")
            
        # Concurrency / Rate-limiting Analysis
        f.write("\n### Concurrency and Rate Limiting Observations\n")
        for name, data in summary.items():
            f.write(f"- **{name}**: ")
            if data["con"]["success_rate"] == 100.0:
                f.write("Handled 5 concurrent requests with 100% stability. No rate limiting observed.\n")
            elif data["con"]["success_rate"] > 0:
                f.write(f"Experienced partial degradation under load: {data['con']['success_rate']:.1f}% success rate. Errors: {list(data['con']['errors'].keys())}\n")
            else:
                f.write("Failed completely under concurrent load. Highly susceptible to rate limiting.\n")

    print(f"\nBenchmark completed. Report written to: {report_path}")


if __name__ == "__main__":
    main()
