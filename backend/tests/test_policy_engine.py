from apps.catalog.entities import LLMModelCandidate
from apps.routing.analyzer import PromptAnalysis
from apps.routing.policy_engine import PolicyEngine


def test_privacy_first_routes_to_local_model_when_sensitive_data_is_detected():
    models = [
        LLMModelCandidate(
            provider="openai",
            name="gpt-4.1-mini",
            role="general",
            quality_level=5,
            speed_level=4,
            cost_level=3,
            privacy_level="external",
            context_window=128000,
        ),
        LLMModelCandidate(
            provider="ollama",
            name="llama3.1:8b",
            role="general",
            quality_level=3,
            speed_level=5,
            cost_level=1,
            privacy_level="local",
            context_window=8192,
        ),
    ]

    result = PolicyEngine().select_model(
        policy_name="privacy-first",
        analysis=PromptAnalysis(
            has_sensitive_data=True,
            is_code=False,
            is_long_context=False,
            requires_reasoning=False,
            estimated_tokens=120,
        ),
        candidates=models,
    )

    assert result.model.provider == "ollama"
    assert result.model.privacy_level == "local"
    assert "sensitive data" in result.reason


def test_quality_first_prefers_highest_quality_reasoning_model():
    models = [
        LLMModelCandidate("ollama", "llama3.1:8b", "general", 3, 5, 1, "local", 8192),
        LLMModelCandidate("ollama", "deepseek-r1:8b", "reasoning", 5, 2, 1, "local", 32768),
    ]

    result = PolicyEngine().select_model(
        policy_name="quality-first",
        analysis=PromptAnalysis(
            has_sensitive_data=False,
            is_code=False,
            is_long_context=False,
            requires_reasoning=True,
            estimated_tokens=200,
        ),
        candidates=models,
    )

    assert result.model.name == "deepseek-r1:8b"
    assert "quality-first" in result.reason


def test_code_prompt_prefers_coding_role_model():
    models = [
        LLMModelCandidate("ollama", "llama3.1:8b", "general", 3, 5, 1, "local", 8192),
        LLMModelCandidate("ollama", "qwen2.5-coder:7b", "coding", 4, 4, 1, "local", 32768),
    ]

    result = PolicyEngine().select_model(
        policy_name="cost-first",
        analysis=PromptAnalysis(
            has_sensitive_data=False,
            is_code=True,
            is_long_context=False,
            requires_reasoning=False,
            estimated_tokens=160,
        ),
        candidates=models,
    )

    assert result.model.name == "qwen2.5-coder:7b"
    assert "coding" in result.reason


def test_policy_config_weights_change_model_ranking():
    models = [
        LLMModelCandidate("ollama", "slow-high-quality", "general", 5, 1, 1, "local", 8192),
        LLMModelCandidate("ollama", "fast-medium-quality", "general", 3, 5, 1, "local", 8192),
    ]

    result = PolicyEngine().select_model(
        policy_name="custom-speed",
        policy_config={
            "quality_weight": 1,
            "speed_weight": 10,
            "cost_weight": 1,
            "context_weight": 0,
            "local_only": False,
        },
        analysis=PromptAnalysis(
            has_sensitive_data=False,
            is_code=False,
            is_long_context=False,
            requires_reasoning=False,
            estimated_tokens=40,
        ),
        candidates=models,
    )

    assert result.model.name == "fast-medium-quality"
    assert "custom policy config" in result.reason
