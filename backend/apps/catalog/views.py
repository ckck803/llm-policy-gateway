import requests
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.audit import record_audit_log
from apps.accounts.permissions import HasScreenAccess
from apps.catalog.provider_models import fetch_provider_models, humanize_model_name
from apps.catalog.models import (
    LLMModel,
    ModelHealthEvent,
    ModelHealthOverride,
    ModelHealthRule,
    ProviderCredential,
    RecoveryStrategy,
    ResponseValidationRule,
    RoutingPolicy,
    RoutingRule,
    ThresholdRule,
    UsageQuota,
)
from apps.catalog.serializers import (
    LLMModelSerializer,
    ModelHealthEventSerializer,
    ModelHealthOverrideSerializer,
    ModelHealthRuleSerializer,
    ProviderCredentialSerializer,
    RecoveryStrategySerializer,
    ResponseValidationRuleSerializer,
    RoutingPolicySerializer,
    RoutingRuleSerializer,
    ThresholdRuleSerializer,
    UsageQuotaSerializer,
)


class AuditCrudMixin:
    audit_resource_type = ""
    audit_name_field = "name"

    def audit_resource_name(self, instance):
        return str(getattr(instance, self.audit_name_field, "") or instance)

    def audit_metadata(self, instance):
        metadata = {}
        for field in ("provider", "name", "rule_id", "strategy_id"):
            if hasattr(instance, field):
                metadata[field] = getattr(instance, field)
        return metadata

    def perform_create(self, serializer):
        instance = serializer.save()
        record_audit_log(
            request=self.request,
            action=f"{self.audit_resource_type}.create",
            resource_type=self.audit_resource_type,
            resource_id=instance.id,
            resource_name=self.audit_resource_name(instance),
            metadata=self.audit_metadata(instance),
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        record_audit_log(
            request=self.request,
            action=f"{self.audit_resource_type}.update",
            resource_type=self.audit_resource_type,
            resource_id=instance.id,
            resource_name=self.audit_resource_name(instance),
            metadata=self.audit_metadata(instance),
        )

    def perform_destroy(self, instance):
        record_audit_log(
            request=self.request,
            action=f"{self.audit_resource_type}.delete",
            resource_type=self.audit_resource_type,
            resource_id=instance.id,
            resource_name=self.audit_resource_name(instance),
            metadata=self.audit_metadata(instance),
        )
        instance.delete()


class LLMModelListView(AuditCrudMixin, generics.ListCreateAPIView):
    queryset = LLMModel.objects.all()
    serializer_class = LLMModelSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "models"
    audit_resource_type = "model"


class LLMModelDetailView(AuditCrudMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LLMModel.objects.all()
    serializer_class = LLMModelSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "models"
    audit_resource_type = "model"


class PolicyListView(AuditCrudMixin, generics.ListCreateAPIView):
    queryset = RoutingPolicy.objects.all()
    serializer_class = RoutingPolicySerializer
    permission_classes = [HasScreenAccess]
    required_screen = "policies"
    audit_resource_type = "policy"


class PolicyDetailView(AuditCrudMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = RoutingPolicy.objects.all()
    serializer_class = RoutingPolicySerializer
    permission_classes = [HasScreenAccess]
    required_screen = "policies"
    audit_resource_type = "policy"


class RoutingRuleListView(AuditCrudMixin, generics.ListCreateAPIView):
    queryset = RoutingRule.objects.all()
    serializer_class = RoutingRuleSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "routing-rules"
    audit_resource_type = "routing_rule"


class RoutingRuleDetailView(AuditCrudMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = RoutingRule.objects.all()
    serializer_class = RoutingRuleSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "routing-rules"
    audit_resource_type = "routing_rule"


class ThresholdRuleListView(AuditCrudMixin, generics.ListCreateAPIView):
    queryset = ThresholdRule.objects.all()
    serializer_class = ThresholdRuleSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "threshold-rules"
    audit_resource_type = "threshold_rule"


class ThresholdRuleDetailView(AuditCrudMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = ThresholdRule.objects.all()
    serializer_class = ThresholdRuleSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "threshold-rules"
    audit_resource_type = "threshold_rule"


class ResponseValidationRuleListView(AuditCrudMixin, generics.ListCreateAPIView):
    queryset = ResponseValidationRule.objects.all()
    serializer_class = ResponseValidationRuleSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "validation-rules"
    audit_resource_type = "validation_rule"


class ResponseValidationRuleDetailView(AuditCrudMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = ResponseValidationRule.objects.all()
    serializer_class = ResponseValidationRuleSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "validation-rules"
    audit_resource_type = "validation_rule"


class RecoveryStrategyListView(AuditCrudMixin, generics.ListCreateAPIView):
    queryset = RecoveryStrategy.objects.all()
    serializer_class = RecoveryStrategySerializer
    permission_classes = [HasScreenAccess]
    required_screen = "recovery-strategies"
    audit_resource_type = "recovery_strategy"


class RecoveryStrategyDetailView(AuditCrudMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = RecoveryStrategy.objects.all()
    serializer_class = RecoveryStrategySerializer
    permission_classes = [HasScreenAccess]
    required_screen = "recovery-strategies"
    audit_resource_type = "recovery_strategy"


class ModelHealthEventListView(generics.ListAPIView):
    queryset = ModelHealthEvent.objects.select_related("rule").all()
    serializer_class = ModelHealthEventSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "health-events"


class ModelHealthOverrideListView(AuditCrudMixin, generics.ListCreateAPIView):
    queryset = ModelHealthOverride.objects.select_related("created_by").all()
    serializer_class = ModelHealthOverrideSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "health-overrides"
    audit_resource_type = "health_override"

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        record_audit_log(
            request=self.request,
            action="health_override.create",
            resource_type="health_override",
            resource_id=instance.id,
            resource_name=instance.name,
            metadata=self.audit_metadata(instance),
        )


class ModelHealthOverrideDetailView(AuditCrudMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = ModelHealthOverride.objects.select_related("created_by").all()
    serializer_class = ModelHealthOverrideSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "health-overrides"
    audit_resource_type = "health_override"


class ProviderCredentialListView(generics.ListCreateAPIView):
    queryset = ProviderCredential.objects.all()
    serializer_class = ProviderCredentialSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "credentials"

    def perform_create(self, serializer):
        credential = serializer.save()
        record_audit_log(
            request=self.request,
            action="credential.create",
            resource_type="provider_credential",
            resource_id=credential.id,
            resource_name=credential.display_name,
            metadata={"provider": credential.provider},
        )


class ProviderCredentialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProviderCredential.objects.all()
    serializer_class = ProviderCredentialSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "credentials"

    def perform_update(self, serializer):
        token_was_rotated = bool(serializer.validated_data.get("access_token"))
        credential = serializer.save()
        record_audit_log(
            request=self.request,
            action="credential.rotate_token" if token_was_rotated else "credential.update",
            resource_type="provider_credential",
            resource_id=credential.id,
            resource_name=credential.display_name,
            metadata={"provider": credential.provider},
        )

    def perform_destroy(self, instance):
        record_audit_log(
            request=self.request,
            action="credential.delete",
            resource_type="provider_credential",
            resource_id=instance.id,
            resource_name=instance.display_name,
            metadata={"provider": instance.provider},
        )
        instance.delete()


class ProviderCredentialTestSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["ollama", "openai", "gemini", "openrouter"])
    base_url = serializers.CharField()
    access_token = serializers.CharField(allow_blank=True, required=False)


class ProviderCredentialTestView(APIView):
    permission_classes = [HasScreenAccess]
    required_screen = "credentials"

    def post(self, request):
        serializer = ProviderCredentialTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.validated_data["provider"]
        base_url = serializer.validated_data["base_url"].rstrip("/")
        access_token = serializer.validated_data.get("access_token", "")

        try:
            response = self.request_provider(provider, base_url, access_token)
            ok = 200 <= response.status_code < 300
            return Response(
                {
                    "ok": ok,
                    "status_code": response.status_code,
                    "message": "Connection succeeded." if ok else self.extract_error_message(response),
                },
                status=status.HTTP_200_OK,
            )
        except requests.RequestException as exc:
            return Response(
                {
                    "ok": False,
                    "status_code": None,
                    "message": str(exc),
                },
                status=status.HTTP_200_OK,
            )

    def request_provider(self, provider: str, base_url: str, access_token: str):
        if provider == "ollama":
            headers = {}
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
            return requests.get(
                f"{base_url}/api/tags",
                headers=headers,
                timeout=15,
            )
        if provider == "gemini":
            return requests.get(
                f"{base_url}/models",
                headers={"x-goog-api-key": access_token},
                timeout=15,
            )
        return requests.get(
            f"{base_url}/models",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )

    def extract_error_message(self, response):
        try:
            payload = response.json()
        except ValueError:
            return response.text[:300] or "Connection failed."
        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                return error.get("message") or str(error)
            if error:
                return str(error)
            return payload.get("message") or str(payload)[:300]
        return str(payload)[:300]


class ProviderModelImportSerializer(serializers.Serializer):
    model_names = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )


class ProviderCredentialModelPreviewView(APIView):
    permission_classes = [HasScreenAccess]
    required_screen = "credentials"

    def get(self, request, pk):
        credential = generics.get_object_or_404(ProviderCredential, pk=pk, is_active=True)
        try:
            models = fetch_provider_models(credential)
        except requests.RequestException as exc:
            record_audit_log(
                request=request,
                action="provider_models.preview_failed",
                resource_type="provider_credential",
                resource_id=credential.id,
                resource_name=credential.display_name,
                metadata={"provider": credential.provider, "error": str(exc)},
            )
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"models": models})


class ProviderCredentialModelImportView(APIView):
    permission_classes = [HasScreenAccess]
    required_screen = "credentials"

    def post(self, request, pk):
        credential = generics.get_object_or_404(ProviderCredential, pk=pk, is_active=True)
        serializer = ProviderModelImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        imported = []
        skipped = []
        for model_name in serializer.validated_data["model_names"]:
            model, created = LLMModel.objects.get_or_create(
                provider=credential.provider,
                name=model_name,
                defaults={
                    "display_name": humanize_model_name(model_name),
                    "model_tier": "standard",
                    "provider_credential": credential,
                    "role": "general",
                    "quality_level": 3,
                    "speed_level": 3,
                    "cost_level": 3,
                    "privacy_level": "external",
                    "context_window": 8192,
                    "input_token_price_per_1m": 0,
                    "output_token_price_per_1m": 0,
                    "average_latency_ms": 0,
                    "timeout_seconds": 120,
                    "is_active": True,
                },
            )
            if created:
                imported.append(LLMModelSerializer(model).data)
            else:
                skipped.append(model_name)
        record_audit_log(
            request=request,
            action="provider_models.import",
            resource_type="provider_credential",
            resource_id=credential.id,
            resource_name=credential.display_name,
            metadata={
                "provider": credential.provider,
                "imported": [model["name"] for model in imported],
                "skipped": skipped,
            },
        )
        return Response({"imported": imported, "skipped": skipped}, status=status.HTTP_201_CREATED)


class UsageQuotaListView(AuditCrudMixin, generics.ListCreateAPIView):
    queryset = UsageQuota.objects.select_related("user").all()
    serializer_class = UsageQuotaSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "quotas"
    audit_resource_type = "usage_quota"


class UsageQuotaDetailView(AuditCrudMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = UsageQuota.objects.select_related("user").all()
    serializer_class = UsageQuotaSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "quotas"
    audit_resource_type = "usage_quota"


class ModelHealthRuleListView(AuditCrudMixin, generics.ListCreateAPIView):
    queryset = ModelHealthRule.objects.all()
    serializer_class = ModelHealthRuleSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "health-rules"
    audit_resource_type = "health_rule"


class ModelHealthRuleDetailView(AuditCrudMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = ModelHealthRule.objects.all()
    serializer_class = ModelHealthRuleSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "health-rules"
    audit_resource_type = "health_rule"
