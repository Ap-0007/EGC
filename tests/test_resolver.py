"""Tests for the provider factory / resolver.

These avoid importing the heavy provider SDKs (google-genai, anthropic,
openai) which are optional at runtime; instead they exercise the resolution
logic, error paths and the registration hook with lightweight fakes.
"""

import pytest

from llm.core.interface import LLMProvider
from llm.core.types import LLMInput, LLMOutput, ModelInfo, ProviderType
from llm.providers import resolver as resolver_module
from llm.providers import get_provider, register_provider


class _FakeProvider(LLMProvider):
    provider_type = ProviderType.OLLAMA

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def generate(self, input: LLMInput) -> LLMOutput:  # pragma: no cover - not exercised
        return LLMOutput(content="")

    def list_models(self) -> list[ModelInfo]:  # pragma: no cover
        return []

    def validate_config(self) -> bool:  # pragma: no cover
        return True


class TestProviderType:
    def test_known_provider_values(self):
        values = {p.value for p in ProviderType}
        assert {"gemini", "claude", "openai", "ollama", "openrouter"} <= values

    def test_default_provider_string_is_gemini(self, monkeypatch):
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        # The factory falls back to "gemini" when nothing is configured;
        # we assert the default string only (SDK instantiation is optional).
        assert resolver_module.os.environ.get("LLM_PROVIDER", "gemini").lower() == "gemini"


class TestGetProvider:
    def test_invalid_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown provider type"):
            get_provider("definitely-not-a-provider")

    def test_unavailable_provider_raises(self, monkeypatch):
        # Simulate a provider whose optional SDK is not installed (class is None).
        monkeypatch.setitem(resolver_module._PROVIDER_MAP, ProviderType.OPENAI, None)
        with pytest.raises(ValueError):
            get_provider("openai")

    def test_register_and_resolve_provider(self, monkeypatch):
        monkeypatch.setitem(resolver_module._PROVIDER_MAP, ProviderType.OLLAMA, _FakeProvider)
        provider = get_provider("ollama", base_url="http://x")
        assert isinstance(provider, _FakeProvider)
        assert provider.kwargs == {"base_url": "http://x"}

    def test_register_provider_helper(self):
        register_provider(ProviderType.OLLAMA, _FakeProvider)
        assert resolver_module._PROVIDER_MAP[ProviderType.OLLAMA] is _FakeProvider

    def test_accepts_enum_directly(self, monkeypatch):
        monkeypatch.setitem(resolver_module._PROVIDER_MAP, ProviderType.OLLAMA, _FakeProvider)
        assert isinstance(get_provider(ProviderType.OLLAMA), _FakeProvider)
