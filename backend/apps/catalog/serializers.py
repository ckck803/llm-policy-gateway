from rest_framework import serializers
from django.utils import timezone

from apps.catalog.health import evaluate_model_health, serialize_model_health_status
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
from apps.catalog.usage import get_quota_usage


class LLMModelSerializer(serializers.ModelSerializer):
    provider_credential_display_name = serializers.CharField(
        source="provider_credential.display_name",
        read_only=True,
        allow_null=True,
    )
    health_status = serializers.SerializerMethodField()
    health_reason = serializers.SerializerMethodField()
    health_metrics = serializers.SerializerMethodField()

    class Meta:
        model = LLMModel
        fields = [
            "id",
            "provider",
            "name",
            "display_name",
            "model_tier",
            "provider_credential",
            "provider_credential_display_name",
            "health_status",
            "health_reason",
            "health_metrics",
            "role",
            "quality_level",
            "speed_level",
            "cost_level",
            "privacy_level",
            "context_window",
            "input_token_price_per_1m",
            "output_token_price_per_1m",
            "average_latency_ms",
            "timeout_seconds",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_health_status(self, instance):
        return evaluate_model_health(provider=instance.provider, model_name=instance.name).status

    def get_health_reason(self, instance):
        return evaluate_model_health(provider=instance.provider, model_name=instance.name).reason

    def get_health_metrics(self, instance):
        return serialize_model_health_status(
            evaluate_model_health(provider=instance.provider, model_name=instance.name)
        )

    def validate(self, attrs):
        provider = attrs.get("provider", getattr(self.instance, "provider", None))
        credential = attrs.get(
            "provider_credential",
            getattr(self.instance, "provider_credential", None),
        )
        if provider == "ollama" and credential is not None:
            raise serializers.ValidationError(
                {"provider_credential": "Local Ollama models do not use provider credentials."}
            )
        if credential is not None and credential.provider != provider:
            raise serializers.ValidationError(
                {"provider_credential": "Credential provider must match the model provider."}
            )
        return attrs


class RoutingPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutingPolicy
        fields = [
            "id",
            "name",
            "display_name",
            "description",
            "priority_config",
            "is_active",
        ]


class RoutingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutingRule
        fields = [
            "id",
            "rule_id",
            "name",
            "description",
            "condition_key",
            "target_tier",
            "priority",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ThresholdRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThresholdRule
        fields = [
            "id",
            "rule_id",
            "name",
            "description",
            "metric_key",
            "operator",
            "threshold_value",
            "action_on_trigger",
            "target_tier",
            "max_tokens",
            "priority",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        action = attrs.get("action_on_trigger", getattr(self.instance, "action_on_trigger", "prefer_tier"))
        target_tier = attrs.get("target_tier", getattr(self.instance, "target_tier", ""))
        max_tokens = attrs.get("max_tokens", getattr(self.instance, "max_tokens", None))
        if action == "prefer_tier" and not target_tier:
            raise serializers.ValidationError({"target_tier": "Target tier is required for prefer_tier action."})
        if action == "set_max_tokens" and max_tokens is None:
            raise serializers.ValidationError({"max_tokens": "Max tokens is required for set_max_tokens action."})
        return attrs


class ResponseValidationRuleSerializer(serializers.ModelSerializer):
    recovery_strategy_display_name = serializers.CharField(
        source="recovery_strategy.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ResponseValidationRule
        fields = [
            "id",
            "rule_id",
            "name",
            "description",
            "recovery_strategy",
            "recovery_strategy_display_name",
            "condition_key",
            "validation_type",
            "action_on_fail",
            "retry_prompt",
            "max_retries",
            "target_tier",
            "priority",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        action = attrs.get("action_on_fail", getattr(self.instance, "action_on_fail", "strict_retry"))
        target_tier = attrs.get("target_tier", getattr(self.instance, "target_tier", ""))
        if action == "escalate" and not target_tier:
            raise serializers.ValidationError({"target_tier": "Target tier is required for escalation."})
        return attrs


class RecoveryStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecoveryStrategy
        fields = [
            "id",
            "strategy_id",
            "name",
            "description",
            "trigger_event",
            "action",
            "retry_prompt",
            "max_retries",
            "target_tier",
            "priority",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        action = attrs.get("action", getattr(self.instance, "action", "strict_retry"))
        target_tier = attrs.get("target_tier", getattr(self.instance, "target_tier", ""))
        if action == "escalate" and not target_tier:
            raise serializers.ValidationError({"target_tier": "Target tier is required for escalation."})
        return attrs


class ModelHealthEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelHealthEvent
        fields = [
            "id",
            "event_type",
            "provider",
            "model_name",
            "status",
            "rule",
            "rule_name",
            "reason",
            "request_count",
            "failures",
            "failure_rate",
            "average_latency_ms",
            "created_at",
        ]


class ModelHealthOverrideSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username", read_only=True, allow_null=True)

    class Meta:
        model = ModelHealthOverride
        fields = [
            "id",
            "name",
            "provider",
            "model_name",
            "override_type",
            "reason",
            "expires_at",
            "is_active",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by"]


class ProviderCredentialSerializer(serializers.ModelSerializer):
    base_url = serializers.CharField(allow_blank=True, write_only=False)
    access_token = serializers.CharField(allow_blank=True, write_only=True, required=False)
    access_token_masked = serializers.SerializerMethodField()

    class Meta:
        model = ProviderCredential
        fields = [
            "id",
            "provider",
            "display_name",
            "base_url",
            "access_token",
            "access_token_masked",
            "last_used_at",
            "token_rotated_at",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["base_url"] = instance.get_base_url()
        return data

    def get_access_token_masked(self, instance):
        token = instance.get_access_token()
        if not token:
            return ""
        if len(token) <= 8:
            return "********"
        return f"{token[:4]}********{token[-4:]}"

    def create(self, validated_data):
        base_url = validated_data.pop("base_url", "")
        access_token = validated_data.pop("access_token", "")
        credential = ProviderCredential(**validated_data)
        credential.set_base_url(base_url)
        credential.set_access_token(access_token)
        credential.save()
        return credential

    def update(self, instance, validated_data):
        base_url = validated_data.pop("base_url", None)
        access_token = validated_data.pop("access_token", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        if base_url is not None:
            instance.set_base_url(base_url)
        if access_token:
            instance.set_access_token(access_token)
            instance.token_rotated_at = timezone.now()
        instance.save()
        return instance


class UsageQuotaSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True, allow_null=True)
    period_start = serializers.SerializerMethodField()
    current_month_requests = serializers.SerializerMethodField()
    current_month_cost_usd = serializers.SerializerMethodField()
    request_usage_ratio = serializers.SerializerMethodField()
    cost_usage_ratio = serializers.SerializerMethodField()
    is_exceeded = serializers.SerializerMethodField()

    class Meta:
        model = UsageQuota
        fields = [
            "id",
            "name",
            "user",
            "username",
            "provider",
            "monthly_request_limit",
            "monthly_cost_limit_usd",
            "period_start",
            "current_month_requests",
            "current_month_cost_usd",
            "request_usage_ratio",
            "cost_usage_ratio",
            "is_exceeded",
            "action_on_exceed",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_usage(self, instance):
        if not hasattr(instance, "_quota_usage"):
            instance._quota_usage = get_quota_usage(instance)
        return instance._quota_usage

    def get_period_start(self, instance):
        return self.get_usage(instance)["period_start"]

    def get_current_month_requests(self, instance):
        return self.get_usage(instance)["current_month_requests"]

    def get_current_month_cost_usd(self, instance):
        return self.get_usage(instance)["current_month_cost_usd"]

    def get_request_usage_ratio(self, instance):
        value = self.get_usage(instance)["request_usage_ratio"]
        return None if value is None else round(float(value), 4)

    def get_cost_usage_ratio(self, instance):
        value = self.get_usage(instance)["cost_usage_ratio"]
        return None if value is None else round(float(value), 4)

    def get_is_exceeded(self, instance):
        return self.get_usage(instance)["is_exceeded"]

    def validate(self, attrs):
        monthly_request_limit = attrs.get(
            "monthly_request_limit",
            getattr(self.instance, "monthly_request_limit", None),
        )
        monthly_cost_limit_usd = attrs.get(
            "monthly_cost_limit_usd",
            getattr(self.instance, "monthly_cost_limit_usd", None),
        )
        if monthly_request_limit is None and monthly_cost_limit_usd is None:
            raise serializers.ValidationError("At least one monthly limit is required.")
        return attrs


class ModelHealthRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelHealthRule
        fields = [
            "id",
            "name",
            "provider",
            "model_name",
            "window_minutes",
            "min_requests",
            "max_failure_rate_percent",
            "max_average_latency_ms",
            "action_on_trigger",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        failure_rate = attrs.get(
            "max_failure_rate_percent",
            getattr(self.instance, "max_failure_rate_percent", None),
        )
        latency = attrs.get(
            "max_average_latency_ms",
            getattr(self.instance, "max_average_latency_ms", None),
        )
        if failure_rate is None and latency is None:
            raise serializers.ValidationError("At least one health threshold is required.")
        return attrs
