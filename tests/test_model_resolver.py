"""Tests for the dynamic model resolution / routing layer.

The EGC runtime must never be coupled to a single hardcoded model: these
tests pin the contract of ModelResolver (registry, aliases, env overrides,
fallback chains, capability routing and the UI strategy description) while
preserving backward compatibility with the legacy symbolic names.
"""

import pytest

from llm.core.model_resolver import ModelCapability, ModelResolver
from llm.core.types import ModelInfo, ProviderType


@pytest.fixture(autouse=True)
def _clean_model_env(monkeypatch):
    for var in ("LLM_MODEL", "EGC_MODEL", "ECC_MODEL", "LLM_PROVIDER", "EGC_EXTRA_MODELS", "ECC_EXTRA_MODELS"):
        monkeypatch.delenv(var, raising=False)
    yield


class TestResolution:
    def test_default_is_gemini(self):
        assert ModelResolver.resolve() == "gemini-2.5-pro"
        assert ModelResolver.default_model("gemini") == "gemini-2.5-pro"

    def test_symbolic_aliases(self):
        assert ModelResolver.resolve("pro") == "gemini-2.5-pro"
        assert ModelResolver.resolve("flash") == "gemini-2.5-flash"
        assert ModelResolver.resolve("flash-lite") == "gemini-2.5-flash-lite"

    def test_legacy_aliases_preserved(self):
        # Older symbolic names and ECC-style tiers must keep resolving.
        assert ModelResolver.resolve("flash-legacy") == "gemini-1.5-flash"
        assert ModelResolver.resolve("ultra") in ModelResolver.list_models("gemini")
        assert ModelResolver.resolve("sonnet") in ModelResolver.list_models("gemini")
        assert ModelResolver.resolve("haiku") in ModelResolver.list_models("gemini")
        assert ModelResolver.resolve("opus") in ModelResolver.list_models("gemini")

    def test_real_id_passthrough(self):
        assert ModelResolver.resolve("gemini-1.5-flash") == "gemini-1.5-flash"
        assert ModelResolver.resolve("gemini-2.0-flash") == "gemini-2.0-flash"
        # Future / experimental / Vertex IDs are passed through untouched.
        assert ModelResolver.resolve("gemini-3.0-pro-exp") == "gemini-3.0-pro-exp"
        assert ModelResolver.resolve("publishers/google/models/gemini-x") == "publishers/google/models/gemini-x"

    def test_unknown_symbolic_falls_back_to_provider_default(self):
        assert ModelResolver.resolve("totally-unknown") == ModelResolver.default_model("gemini")

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL", "gemini-1.5-pro")
        assert ModelResolver.resolve() == "gemini-1.5-pro"
        # Legacy env var name is still honored (compat constitution).
        monkeypatch.delenv("LLM_MODEL", raising=False)
        monkeypatch.setenv("ECC_MODEL", "gemini-1.5-flash")
        assert ModelResolver.resolve() == "gemini-1.5-flash"

    def test_env_alias_override(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL", "flash")
        assert ModelResolver.resolve() == "gemini-2.5-flash"

    def test_explicit_hint_beats_env(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL", "gemini-1.5-flash")
        assert ModelResolver.resolve("gemini-2.5-pro") == "gemini-2.5-pro"

    def test_env_only_applies_to_matching_provider(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL", "gemini-2.5-flash")
        # A Gemini env model must not leak into the Claude provider default.
        assert ModelResolver.default_model("claude") == "claude-sonnet-4-7"
        assert ModelResolver.default_model("gemini") == "gemini-2.5-flash"


class TestFallbacks:
    def test_chain_is_acyclic_and_terminates(self):
        for model_id in ModelResolver.list_models("gemini"):
            chain = ModelResolver.fallback_chain(model_id)
            assert model_id not in chain
            assert len(chain) == len(set(chain))

    def test_pro_degrades_to_flash_then_legacy(self):
        chain = ModelResolver.fallback_chain("gemini-2.5-pro")
        assert chain[0] == "gemini-2.5-flash"
        assert "gemini-1.5-flash" in chain

    def test_fallback_map_covers_registry(self):
        mapping = ModelResolver.fallback_map()
        # Every non-terminal model points at another known model.
        for src, dst in mapping.items():
            assert dst in ModelResolver._REGISTRY

    def test_fallback_for_unknown_model(self):
        info = ModelResolver.get_model_info("gemini-9.9-superflash")
        assert info["provider"] == "gemini"
        assert info["fallback"] in ModelResolver._REGISTRY
        assert info.get("unknown") is True

    def test_get_fallback_backward_compat(self):
        assert ModelResolver.get_fallback("gemini-1.5-flash-8b") is None
        assert ModelResolver.get_fallback("gemini-2.5-pro") == "gemini-2.5-flash"


class TestCapabilities:
    def test_reasoning_models(self):
        assert ModelResolver.supports("gemini-2.5-pro", ModelCapability.REASONING)
        assert ModelResolver.supports("gemini-1.5-pro", ModelCapability.REASONING)

    def test_pick_by_capability(self):
        assert ModelResolver.pick_by_capability(ModelCapability.REASONING, "gemini") == "gemini-2.5-pro"
        picked = ModelResolver.pick_by_capability(ModelCapability.LOW_LATENCY, "gemini")
        assert ModelCapability.LOW_LATENCY in ModelResolver.capabilities(picked)

    def test_pick_by_capability_falls_back_to_default(self):
        # No ollama model advertises MULTIMODAL -> default model.
        assert ModelResolver.pick_by_capability(ModelCapability.MULTIMODAL, "ollama") == ModelResolver.default_model("ollama")


class TestListing:
    def test_list_models_filters_by_provider(self):
        gemini = ModelResolver.list_models("gemini")
        assert "gemini-2.5-pro" in gemini
        assert all(m.startswith(("gemini-",)) for m in gemini)
        assert "claude-sonnet-4-7" in ModelResolver.list_models("claude")

    def test_env_extra_models(self, monkeypatch):
        monkeypatch.setenv("EGC_EXTRA_MODELS", "gemini-4.0-flash-exp, gemini-4.0-pro-exp")
        gemini = ModelResolver.list_models("gemini")
        assert "gemini-4.0-flash-exp" in gemini
        assert "gemini-4.0-pro-exp" in gemini

    def test_model_infos_returns_modelinfo(self):
        infos = ModelResolver.model_infos("gemini")
        assert infos and all(isinstance(i, ModelInfo) for i in infos)
        assert all(i.provider == ProviderType.GEMINI for i in infos)

    def test_list_available_models_keeps_legacy_names(self):
        names = ModelResolver.list_available_models()
        for legacy in ("pro", "flash", "flash-legacy", "ultra"):
            assert legacy in names


class TestOpenRouter:
    def test_default_and_alias(self):
        assert ModelResolver.default_model("openrouter") == "openrouter/auto"
        assert ModelResolver.resolve("openrouter") == "openrouter/auto"

    def test_vendor_model_passthrough(self):
        # Any "vendor/model" ID is accepted directly (broker semantics).
        assert ModelResolver.resolve("meta-llama/llama-3.1-70b-instruct") == "meta-llama/llama-3.1-70b-instruct"
        assert ModelResolver.resolve("anthropic/claude-sonnet-4.5") == "anthropic/claude-sonnet-4.5"

    def test_provider_inference_for_vendor_model(self):
        assert ModelResolver._provider_for("google/gemini-2.5-pro") == "openrouter"
        assert ModelResolver._provider_for("meta-llama/llama-3.1-70b") == "openrouter"
        # Vertex fully-qualified paths stay on gemini, not openrouter.
        assert ModelResolver._provider_for("publishers/google/models/gemini-x") == "gemini"

    def test_registry_and_listing(self):
        ids = ModelResolver.list_models("openrouter")
        assert "openrouter/auto" in ids
        assert all("/" in m for m in ids)
        infos = ModelResolver.model_infos("openrouter")
        assert infos and all(i.provider == ProviderType.OPENROUTER for i in infos)

    def test_strategy_label(self):
        d = ModelResolver.describe_strategy("openrouter/auto")
        assert d["provider"] == "OpenRouter (broker)"
        assert d["provider_id"] == "openrouter"


class TestStrategyDescription:
    def test_dynamic_routing_when_no_hint(self):
        d = ModelResolver.describe_strategy()
        assert d["provider"] == "Google Gemini"
        assert d["strategy"] == "Dynamic Routing"
        assert d["preferred_capability"] == "reasoning"
        assert d["resolved_model"] == "gemini-2.5-pro"
        assert "->" in d["fallback_chain"]

    def test_explicit_model_strategy(self):
        d = ModelResolver.describe_strategy("gemini-2.5-pro")
        assert "Explicit model" in d["strategy"]

    def test_legacy_tier_hint_is_routed_not_pinned(self):
        d = ModelResolver.describe_strategy("sonnet")
        assert d["strategy"] == "Dynamic Routing"
        assert d["resolved_model"] in ModelResolver.list_models("gemini")

    def test_env_pinned_strategy(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL", "gemini-1.5-pro")
        d = ModelResolver.describe_strategy()
        assert d["strategy"] == "Pinned via environment"
        assert d["resolved_model"] == "gemini-1.5-pro"
