from dataclasses import dataclass
from typing import Iterable, Optional

from apps.catalog.entities import LLMModelCandidate
from apps.routing.analyzer import PromptAnalysis


@dataclass(frozen=True)
class RoutingDecision:
    model: LLMModelCandidate
    reason: str


class PolicyEngine:
    # 정책 엔진은 의도적으로 provider에 의존하지 않습니다. 모델 메타데이터만 보고
    # 판단하므로, 나중에 OpenAI/Gemini를 추가해도 라우팅 규칙은 크게 바뀌지 않습니다.
    def select_model(
        self,
        *,
        policy_name: str,
        policy_config: Optional[dict] = None,
        analysis: PromptAnalysis,
        candidates: Iterable[LLMModelCandidate],
    ) -> RoutingDecision:
        policy_config = policy_config or {}
        available = list(candidates)
        if not available:
            raise ValueError("No active LLM models are available.")

        filtered = available
        reasons = []

        # 개인정보 제약은 capability 점수 계산보다 먼저 적용합니다. 민감한 프롬프트가
        # 점수가 높다는 이유만으로 외부 모델에 전달되는 일을 막기 위해서입니다.
        requires_local = analysis.has_sensitive_data or policy_name == "privacy-first" or policy_config.get("local_only")
        if requires_local:
            local_models = [model for model in filtered if model.privacy_level == "local"]
            if local_models:
                filtered = local_models
                if analysis.has_sensitive_data:
                    reasons.append("sensitive data requires a local model")
                elif policy_config.get("local_only"):
                    reasons.append("policy config requires a local model")
                else:
                    reasons.append("privacy-first policy requires a local model")

        # 프롬프트 신호로 후보군을 먼저 좁힙니다. 이후 ranking은 서로 무관한 모델을
        # 비교하지 않고, 필요한 capability 범위 안에서 최적 모델을 고릅니다.
        if analysis.is_code:
            coding_models = [model for model in filtered if model.role == "coding"]
            if coding_models:
                filtered = coding_models
                reasons.append("coding prompt matched coding-specialized models")

        if analysis.is_long_context:
            required_window = max(analysis.estimated_tokens * 2, 8192)
            long_context_models = [
                model for model in filtered if model.context_window >= required_window
            ]
            if long_context_models:
                filtered = long_context_models
                reasons.append("long prompt matched models with larger context windows")

        if analysis.requires_reasoning:
            reasoning_models = [model for model in filtered if model.role == "reasoning"]
            if reasoning_models:
                filtered = reasoning_models
                reasons.append("reasoning prompt matched reasoning-specialized models")

        selected = self._rank(policy_name, filtered, policy_config)[0]
        if not reasons:
            if policy_config:
                reasons.append(f"{policy_name} custom policy config selected the best ranked active model")
            else:
                reasons.append(f"{policy_name} selected the best ranked active model")
        else:
            if policy_config:
                reasons.append(f"{policy_name} custom policy config selected the final model")
            else:
                reasons.append(f"{policy_name} ranking selected the final model")

        return RoutingDecision(model=selected, reason="; ".join(reasons))

    def _rank(self, policy_name: str, models: list[LLMModelCandidate], policy_config: dict):
        if policy_config:
            # 관리자 화면에서 입력한 가중치로 custom policy 점수를 계산합니다.
            # quality/speed/context는 점수를 올리고, cost는 점수를 낮춥니다.
            quality_weight = int(policy_config.get("quality_weight", 1))
            speed_weight = int(policy_config.get("speed_weight", 1))
            cost_weight = int(policy_config.get("cost_weight", 1))
            context_weight = int(policy_config.get("context_weight", 0))
            return sorted(
                models,
                key=lambda model: -(
                    (model.quality_level * quality_weight)
                    + (model.speed_level * speed_weight)
                    - (model.cost_level * cost_weight)
                    + ((model.context_window // 8192) * context_weight)
                ),
            )

        # 기본 정책은 초기 실행 시에도 예측 가능한 결과를 주기 위한 fallback입니다.
        if policy_name == "quality-first":
            return sorted(
                models,
                key=lambda model: (
                    -model.quality_level,
                    model.cost_level,
                    -model.speed_level,
                    -model.context_window,
                ),
            )
        if policy_name == "privacy-first":
            return sorted(
                models,
                key=lambda model: (
                    model.privacy_level != "local",
                    model.cost_level,
                    -model.quality_level,
                    -model.speed_level,
                ),
            )
        return sorted(
            models,
            key=lambda model: (
                model.cost_level,
                -model.speed_level,
                -model.quality_level,
                -model.context_window,
            ),
        )
