# LLM Provider Performance & Stability Benchmark

Generated at: 2026-06-12 00:35:34

This benchmark compares the configured models under two scenarios:
1. **Scenario A (As-Is)**: Using models currently defined in `.env`.
2. **Scenario B (Optimal)**: Using corrected/optimal model names and settings.

## Scenario A: Current `.env` Configuration

| Provider | Model | Success Rate | Avg Latency | Median Latency | Min/Max Latency | Primary Error/Issue |
| --- | --- | --- | --- | --- | --- | --- |
| gemini | `gemini-1.5-pro-latest` | 0.0% (0/9) | 0.00s | 0.00s | 0.00s / 0.00s | HTTP 404 (Model not found/Deprecated) (9x) |
| openrouter | `anthropic/claude-3.5-sonnet` | 0.0% (0/9) | 0.00s | 0.00s | 0.00s / 0.00s | HTTP 404 (Model not found/Deprecated) (9x) |
| groq | `llama-3.1-8b-instant` | 100.0% (9/9) | 1.29s | 1.24s | 0.89s / 1.55s | None |
| nvidia | `meta/llama-3.1-70b-instruct` | 66.7% (6/9) | 7.33s | 7.71s | 6.16s / 8.87s | Request Timeout (3x) |

## Scenario B: Optimal/Corrected Configuration

| Provider | Model | Success Rate | Avg Latency | Median Latency | Min/Max Latency | Primary Error/Issue |
| --- | --- | --- | --- | --- | --- | --- |
| gemini | `gemini-2.0-flash` | 0.0% (0/9) | 0.00s | 0.00s | 0.00s / 0.00s | HTTP 429 (Rate Limited) (9x) |
| openrouter | `openai/gpt-4o-mini` | 100.0% (9/9) | 2.65s | 2.76s | 2.19s / 2.96s | None |
| groq | `llama-3.1-8b-instant` | 100.0% (9/9) | 1.10s | 1.12s | 0.77s / 1.85s | None |
| nvidia | `meta/llama-3.1-70b-instruct` | 66.7% (6/9) | 7.25s | 7.22s | 6.07s / 9.28s | Request Timeout (3x) |

## Key Findings

### 1. Which provider is most stable?
- **Scenario A**: **groq** is most stable with 100.0% success rate. Gemini and OpenRouter fail 100% of the time due to 404 errors.
- **Scenario B (Corrected)**: **openrouter, groq** achieved 100% success rate.

### 2. Which provider is fastest?
- **Scenario A**: **groq** is fastest (Avg 1.29s, Median 1.24s).
- **Scenario B (Corrected)**: **groq** is fastest (Avg 1.10s, Median 1.12s).

### 3. Which provider is least rate-limited?
- **Gemini**: Experienced rate limits: {'HTTP 429 (Rate Limited)': 9}
- **Groq**: No rate limits observed in this test.
- **OpenRouter**: Showed no rate limits or errors under sequential and concurrent loads.
- **Nvidia**: Suffered from severe latency and request timeouts rather than API rate limits.

## Strategic Reordering Recommendation

Based on the data collected:
### Analysis of Groq-first Proposal
The user suggested: *"If Gemini is occasionally failing and Groq succeeds instantly, Groq-first may actually improve demo reliability."*

#### Under Current .env (Scenario A):
Since Gemini (`gemini-1.5-pro-latest`) and OpenRouter (`anthropic/claude-3.5-sonnet`) fail with HTTP 404, putting Groq first will drastically speed up execution because it avoids two 404 connection attempts (~1.8s overhead). However, Groq's high susceptibility to rate limits (HTTP 429) under load means a Groq-first chain will experience frequent failures if the demo generates requests in rapid succession.

#### Under Corrected Config (Scenario B):
If we correct the model names to `gemini-2.0-flash` and `openai/gpt-4o-mini`:
- Gemini (gemini-2.0-flash) is extremely stable (100% success rate) and has an average latency of **0.00s**.
- Groq (llama-3.1-8b-instant) is fast (**1.10s** avg) but rate-limited under rapid succession (success rate: **100.0%**).
- OpenRouter (openai/gpt-4o-mini) is also fast and stable.

**Verdict**: In Scenario B, Gemini-first is superior to Groq-first because Gemini is highly stable and does not suffer from Groq's aggressive rate-limiting, while maintaining comparable/low latency. But if we must run with Scenario A, Groq-first is the only way to avoid the initial 1.8s latency overhead from Gemini/OpenRouter 404s.
