# Provider Benchmark Results

Generated at: 2026-06-12 01:57:03

## Overview of Provider Metrics

| Provider | Model | Seq Success | Seq Avg Latency | Con Success | Con Avg Latency | Combined Success | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gemini | `gemini-1.5-pro-latest` | 0.0% (0/8) | 0.00s | 0.0% (0/5) | 0.00s | 0.0% | HTTPStatusError: Client error '404 Not Found' for url 'https://generativelanguag... (13x) |
| openrouter | `anthropic/claude-3.5-sonnet` | 0.0% (0/8) | 0.00s | 0.0% (0/5) | 0.00s | 0.0% | HTTPStatusError: Client error '404 Not Found' for url 'https://openrouter.ai/api... (13x) |
| groq | `llama-3.1-8b-instant` | 100.0% (8/8) | 0.75s | 100.0% (5/5) | 0.96s | 100.0% | None |
| nvidia | `meta/llama-3.1-70b-instruct` | 75.0% (6/8) | 5.34s | 60.0% (3/5) | 6.15s | 69.2% | ReadTimeout: The read operation timed out (4x) |

## Latency Statistics (Combined Seq + Con)

| Provider | Min Latency | Median Latency | Max Latency | Avg Latency |
| --- | --- | --- | --- | --- |
| gemini | 0.00s | 0.00s | 0.00s | 0.00s |
| openrouter | 0.00s | 0.00s | 0.00s | 0.00s |
| groq | 0.58s | 0.80s | 1.00s | 0.83s |
| nvidia | 3.57s | 5.70s | 7.81s | 5.61s |

## Detailed Analysis and Verdicts

- **Fastest Provider**: groq (Avg 0.83s)
- **Most Stable Provider**: groq (100.0% success rate)

### Concurrency and Rate Limiting Observations
- **gemini**: Failed completely under concurrent load. Highly susceptible to rate limiting.
- **openrouter**: Failed completely under concurrent load. Highly susceptible to rate limiting.
- **groq**: Handled 5 concurrent requests with 100% stability. No rate limiting observed.
- **nvidia**: Experienced partial degradation under load: 60.0% success rate. Errors: ['ReadTimeout: The read operation timed out']
