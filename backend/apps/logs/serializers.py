from rest_framework import serializers

from apps.logs.models import RoutingLog


class RoutingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutingLog
        fields = [
            "id",
            "prompt_summary",
            "policy",
            "selected_provider",
            "selected_model",
            "routing_reason",
            "latency_ms",
            "estimated_tokens",
            "response_text",
            "error_message",
            "created_at",
        ]
