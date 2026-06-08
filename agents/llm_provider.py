"""
Unified LLM provider layer for ConflictSense.

Inference order is intentionally non-Azure:
Gemini -> OpenRouter -> Groq -> NVIDIA NIM -> Tier 3 mock mode.
Agents call this module through one interface so provider failures never leak
into reasoning code or terminate the demo pipeline.
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
            "max_tokens": 2048,
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
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 2048},
        }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"
        with httpx.Client(timeout=self.timeout_s) as client:
            response = client.post(url, json=payload)
            if response.status_code in {408, 409, 425, 429, 500, 502, 503, 504}:
                raise LLMProviderError(f"Gemini transient failure: HTTP {response.status_code}")
            response.raise_for_status()
            data = response.json()
        parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
        content = "".join(str(part.get("text", "")) for part in parts).strip()
        if not content:
            raise LLMProviderError("Gemini returned an empty response")
        return LLMResponse(content, self.name, self.model, time.monotonic() - started)


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    base_url = "https://openrouter.ai/api/v1"

    def __init__(self) -> None:
        super().__init__(
            os.getenv("OPENROUTER_API_KEY", ""),
            os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            float(os.getenv("LLM_TIMEOUT_S", "12")),
        )


class GroqProvider(OpenAICompatibleProvider):
    name = "groq"
    base_url = "https://api.groq.com/openai/v1"

    def __init__(self) -> None:
        super().__init__(
            os.getenv("GROQ_API_KEY", ""),
            os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
            float(os.getenv("LLM_TIMEOUT_S", "12")),
        )


class NvidiaProvider(OpenAICompatibleProvider):
    name = "nvidia"
    base_url = "https://integrate.api.nvidia.com/v1"

    def __init__(self) -> None:
        super().__init__(
            os.getenv("NVIDIA_API_KEY", "") or os.getenv("NVIDIA_NIM_API_KEY", ""),
            os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct"),
            float(os.getenv("LLM_TIMEOUT_S", "12")),
        )


class ProviderChain:
    def __init__(self, providers: Optional[list[LLMProvider]] = None) -> None:
        self.providers = providers or [
            GeminiProvider(),
            OpenRouterProvider(),
            GroqProvider(),
            NvidiaProvider(),
        ]

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        json_mode: bool = False,
        mock_factory: Optional[Callable[[], str | dict[str, Any]]] = None,
    ) -> LLMResponse:
        if os.getenv("CONFLICTSENSE_FORCE_MOCK", "").lower() in {"1", "true", "yes"}:
            if mock_factory is None:
                raise LLMProviderError("Forced mock mode but no mock fallback was supplied.")
            content = mock_factory()
            if not isinstance(content, str):
                content = json.dumps(content)
            return LLMResponse(content=content, provider="mock", model="tier-3", elapsed_s=0.0, is_mock_mode=True)

        for provider in self.providers:
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
                logger.warning("LLM provider %s failed: %s", provider.name, exc)

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
    ) -> tuple[dict[str, Any], LLMResponse]:
        response = self.complete(system_prompt, user_prompt, json_mode=True, mock_factory=mock_factory)
        return _parse_json(response.content), response

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        mock_factory: Callable[[], str],
    ) -> LLMResponse:
        return self.complete(system_prompt, user_prompt, json_mode=False, mock_factory=mock_factory)


def _parse_json(raw_text: str) -> dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw_text[start : end + 1])
        raise


_default_chain: ProviderChain | None = None


def get_provider_chain() -> ProviderChain:
    global _default_chain
    if _default_chain is None:
        _default_chain = ProviderChain()
    return _default_chain
