"""
Unified LLM provider layer for ConflictSense.

Provider priority: Groq (fast) → Nvidia (reliable) → Mock (Tier 3).
OpenRouter has been removed — it returns 402 Payment Required.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("conflictsense.llm_provider")

# Groq 429 retry config
_GROQ_MAX_RETRIES = 2
_GROQ_RETRY_DELAY_S = 2.0


class LLMProviderError(RuntimeError):
    """Raised when a provider returns no usable response."""


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    elapsed_s: float
    is_mock_mode: bool = False


class LLMProvider:
    name = "base"

    def __init__(self, api_key: str, model: str, timeout_s: float = 12.0) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_s = timeout_s

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def complete(self, system_prompt: str, user_prompt: str, *, json_mode: bool) -> LLMResponse:
        raise NotImplementedError


class OpenAICompatibleProvider(LLMProvider):
    base_url = ""

    def _payload(self, system_prompt: str, user_prompt: str, json_mode: bool) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
            "max_tokens": 512,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        return payload

    def complete(self, system_prompt: str, user_prompt: str, *, json_mode: bool) -> LLMResponse:
        if not self.available:
            raise LLMProviderError(f"{self.name} is not configured")
        started = time.monotonic()
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=self.timeout_s) as client:
            response = client.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=self._payload(system_prompt, user_prompt, json_mode),
            )
            if response.status_code in {408, 409, 425, 429, 500, 502, 503, 504}:
                raise LLMProviderError(f"{self.name} transient failure: HTTP {response.status_code}")
            if response.status_code >= 400:
                print(f"[{self.name}] Error {response.status_code}: {response.text}")
            response.raise_for_status()
            data = response.json()
        content = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        if not content.strip():
            raise LLMProviderError(f"{self.name} returned an empty response")
        return LLMResponse(content.strip(), self.name, self.model, time.monotonic() - started)


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self) -> None:
        super().__init__(
            os.getenv("GEMINI_API_KEY", ""),
            os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            float(os.getenv("LLM_TIMEOUT_S", "12")),
        )

    def complete(self, system_prompt: str, user_prompt: str, *, json_mode: bool) -> LLMResponse:
        if not self.available:
            raise LLMProviderError("Gemini is not configured")
        started = time.monotonic()
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        payload: dict[str, Any] = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 1024},
        }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"
        with httpx.Client(timeout=self.timeout_s) as client:
            response = client.post(url, json=payload)
            if response.status_code in {408, 409, 425, 429, 500, 502, 503, 504}:
                raise LLMProviderError(f"Gemini transient failure: HTTP {response.status_code}")
            if response.status_code >= 400:
                print(f"[gemini] Error {response.status_code}: {response.text}")
            response.raise_for_status()
            data = response.json()
        parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
        content = "".join(str(part.get("text", "")) for part in parts).strip()
        if not content:
            raise LLMProviderError("Gemini returned an empty response")
        return LLMResponse(content, self.name, self.model, time.monotonic() - started)


class GroqProvider(OpenAICompatibleProvider):
    """Groq with automatic 429 retry (up to _GROQ_MAX_RETRIES times)."""
    name = "groq"
    base_url = "https://api.groq.com/openai/v1"

    def __init__(self) -> None:
        super().__init__(
            os.getenv("GROQ_API_KEY", ""),
            os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            float(os.getenv("LLM_TIMEOUT_S", "8.0")),
        )

    def complete(self, system_prompt: str, user_prompt: str, *, json_mode: bool) -> LLMResponse:
        last_exc: Exception | None = None
        for attempt in range(_GROQ_MAX_RETRIES + 1):
            try:
                return super().complete(system_prompt, user_prompt, json_mode=json_mode)
            except LLMProviderError as exc:
                if "429" in str(exc) and attempt < _GROQ_MAX_RETRIES:
                    logger.info("Groq 429 — retrying in %.1fs (attempt %d/%d)", _GROQ_RETRY_DELAY_S, attempt + 1, _GROQ_MAX_RETRIES)
                    time.sleep(_GROQ_RETRY_DELAY_S)
                    last_exc = exc
                else:
                    raise
        raise last_exc  # type: ignore[misc]


class NvidiaProvider(OpenAICompatibleProvider):
    name = "nvidia"
    base_url = "https://integrate.api.nvidia.com/v1"

    def __init__(self) -> None:
        super().__init__(
            os.getenv("NVIDIA_API_KEY", "") or os.getenv("NVIDIA_NIM_API_KEY", ""),
            os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct"),
            float(os.getenv("LLM_TIMEOUT_S", "15.0")),
        )


class ProviderChain:
    def __init__(self, providers: Optional[list[LLMProvider]] = None) -> None:
        self.providers = providers or [
            GroqProvider(),
            NvidiaProvider(),
            # GeminiProvider(),  # 404 on embeddings endpoint; disabled
        ]

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        json_mode: bool = False,
        mock_factory: Optional[Callable[[], str | dict[str, Any]]] = None,
        allow_mock: bool = True,
    ) -> LLMResponse:
        if os.getenv("CONFLICTSENSE_FORCE_MOCK", "").lower() in {"1", "true", "yes"}:
            if not allow_mock:
                raise LLMProviderError("Mock fallback forbidden in strict live mode.")
            if mock_factory is None:
                raise LLMProviderError("Forced mock mode but no mock fallback was supplied.")
            content = mock_factory()
            if not isinstance(content, str):
                content = json.dumps(content)
            return LLMResponse(content=content, provider="mock", model="tier-3", elapsed_s=0.0, is_mock_mode=True)

        for provider in self.providers:
            from unittest.mock import Mock, MagicMock
            is_mock = isinstance(provider, (Mock, MagicMock))
            if "PYTEST_CURRENT_TEST" in os.environ and not is_mock:
                logger.info("Bypassing live LLM provider %s in test environment", provider.name)
                continue
            if not provider.available:
                logger.info("LLM provider %s not configured; skipping.", provider.name)
                continue
            try:
                response = provider.complete(system_prompt, user_prompt, json_mode=json_mode)
                if json_mode:
                    _parse_json(response.content)
                logger.info("LLM provider %s succeeded in %.2fs.", provider.name, response.elapsed_s)
                return response
            except Exception as exc:
                logger.warning("LLM provider %s failed: %s — reason: %s", provider.name, type(exc).__name__, exc)

        if not allow_mock:
            raise LLMProviderError("All LLM providers failed and mock fallback is forbidden.")
        if mock_factory is None:
            raise LLMProviderError("All LLM providers failed and no mock fallback was supplied.")
        content = mock_factory()
        if not isinstance(content, str):
            content = json.dumps(content)
        return LLMResponse(content=content, provider="mock", model="tier-3", elapsed_s=0.0, is_mock_mode=True)

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        mock_factory: Callable[[], str | dict[str, Any]],
        allow_mock: bool = True,
    ) -> tuple[dict[str, Any], LLMResponse]:
        response = self.complete(
            system_prompt,
            user_prompt,
            json_mode=True,
            mock_factory=mock_factory,
            allow_mock=allow_mock,
        )
        return _parse_json(response.content), response

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        mock_factory: Callable[[], str],
        allow_mock: bool = True,
    ) -> LLMResponse:
        return self.complete(
            system_prompt,
            user_prompt,
            json_mode=False,
            mock_factory=mock_factory,
            allow_mock=allow_mock,
        )


def _parse_json(raw_text: str) -> dict[str, Any]:
    """Parse JSON with brace-extraction fallback for markdown fences and preamble text."""
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start >= 0 and end > start:
            logger.debug("_parse_json: extracting JSON from chars %d:%d", start, end + 1)
            data = json.loads(raw_text[start : end + 1])
        else:
            logger.warning(
                "_parse_json: no JSON object found (len=%d, preview=%r)",
                len(raw_text), raw_text[:120],
            )
            raise

    if not isinstance(data, dict):
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            logger.debug("_parse_json: top-level array — using first element.")
            data = data[0]
        else:
            raise ValueError(f"Expected JSON object (dict), got {type(data).__name__}")
    return data


_default_chain: ProviderChain | None = None


def get_provider_chain() -> ProviderChain:
    """Return the module-level singleton ProviderChain."""
    global _default_chain
    if _default_chain is None:
        _default_chain = ProviderChain()
    return _default_chain


def reset_provider_chain() -> None:
    """Invalidate the singleton so tests can re-initialise with new env vars."""
    global _default_chain
    _default_chain = None
