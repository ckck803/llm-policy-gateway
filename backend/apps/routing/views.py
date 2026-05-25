import time

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasScreenAccess
from apps.catalog.models import LLMModel, RoutingPolicy
from apps.logs.models import RoutingLog
from apps.logs.serializers import RoutingLogSerializer
from apps.providers.registry import ProviderRegistry
from apps.routing.analyzer import PromptAnalyzer
from apps.routing.policy_engine import PolicyEngine


class ChatRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(allow_blank=False)
    policy = serializers.SlugField(default="cost-first")


class ChatView(APIView):
    permission_classes = [HasScreenAccess]
    required_screen = "playground"

    # 이 객체들은 요청별 상태를 갖지 않습니다. view class에 한 번만 만들어두면
    # 매 요청마다 새로 생성하지 않아도 되고, 요청 상태가 섞일 위험도 없습니다.
    analyzer = PromptAnalyzer()
    policy_engine = PolicyEngine()
    provider_registry = ProviderRegistry()

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prompt = serializer.validated_data["prompt"]
        policy = serializer.validated_data["policy"]

        # 정책은 관리자 화면에서 수정됩니다. chat endpoint는 항상 DB의 active 정책을
        # 읽기 때문에 서버 재시작 없이 변경 사항이 바로 적용됩니다.
        policy_record = RoutingPolicy.objects.filter(name=policy, is_active=True).first()
        if not policy_record:
            return Response(
                {"detail": f"Routing policy '{policy}' is not active or does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_models = list(LLMModel.objects.filter(is_active=True))
        analysis = self.analyzer.analyze(prompt)

        # 먼저 모델 메타데이터로 라우팅 결정을 내리고, 그 다음 선택된 provider를 호출합니다.
        # provider 호출이 실패해도 어떤 기준으로 모델이 선택됐는지 로그로 남길 수 있습니다.
        decision = self.policy_engine.select_model(
            policy_name=policy,
            policy_config=policy_record.priority_config,
            analysis=analysis,
            candidates=[model.to_candidate() for model in active_models],
        )

        started = time.perf_counter()
        response_text = ""
        error_message = ""
        response_status = status.HTTP_200_OK

        try:
            # provider 구현체는 벤더별 HTTP 형식을 공통 chat interface 뒤로 숨깁니다.
            # 현재는 Ollama만 연결되어 있고, 이후 OpenAI/Gemini adapter를 추가할 수 있습니다.
            provider = self.provider_registry.get(decision.model.provider)
            llm_response = provider.chat(
                model=decision.model.name,
                messages=[{"role": "user", "content": prompt}],
                options={},
            )
            response_text = llm_response.text
        except Exception as exc:
            error_message = str(exc)
            response_status = status.HTTP_502_BAD_GATEWAY

        latency_ms = int((time.perf_counter() - started) * 1000)

        # provider 호출 성공/실패를 모두 기록합니다. catalog에는 등록됐지만 Ollama에
        # 설치되지 않은 모델을 찾을 때 실패 로그가 특히 유용합니다.
        log = RoutingLog.objects.create(
            prompt_summary=prompt[:240],
            policy=policy,
            selected_provider=decision.model.provider,
            selected_model=decision.model.name,
            routing_reason=decision.reason,
            latency_ms=latency_ms,
            estimated_tokens=analysis.estimated_tokens,
            response_text=response_text,
            error_message=error_message,
        )

        payload = RoutingLogSerializer(log).data
        payload["analysis"] = {
            "has_sensitive_data": analysis.has_sensitive_data,
            "is_code": analysis.is_code,
            "is_long_context": analysis.is_long_context,
            "requires_reasoning": analysis.requires_reasoning,
            "estimated_tokens": analysis.estimated_tokens,
        }
        return Response(payload, status=response_status)
