from datetime import datetime, time, timedelta

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasScreenAccess
from apps.catalog.health import evaluate_model_health, serialize_model_health_status
from apps.catalog.models import LLMModel, ModelHealthEvent
from apps.logs.models import RoutingLog
from apps.logs.serializers import RoutingLogSerializer


class DashboardMetricsView(APIView):
    permission_classes = [HasScreenAccess]
    required_screen = "dashboard"

    def get_filtered_logs(self, request):
        logs = RoutingLog.objects.select_related("user").all()
        period = request.query_params.get("period", "7d")
        today = timezone.localdate()
        start_date = None
        end_date = None

        if period == "today":
            start_date = today
            end_date = today
        elif period == "30d":
            start_date = today - timedelta(days=29)
            end_date = today
        elif period == "custom":
            start_date = parse_date(request.query_params.get("start_date", ""))
            end_date = parse_date(request.query_params.get("end_date", ""))
        elif period == "all":
            return logs, {"period": period, "start_date": None, "end_date": None}
        else:
            period = "7d"
            start_date = today - timedelta(days=6)
            end_date = today

        if start_date:
            start_at = timezone.make_aware(
                datetime.combine(start_date, time.min)
            )
            logs = logs.filter(created_at__gte=start_at)
        if end_date:
            end_at = timezone.make_aware(
                datetime.combine(end_date + timedelta(days=1), time.min)
            )
            logs = logs.filter(created_at__lt=end_at)

        return logs, {
            "period": period,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        }

    def get(self, request):
        logs, active_filter = self.get_filtered_logs(request)
        total_requests = logs.count()
        average_latency = logs.aggregate(value=Avg("latency_ms"))["value"] or 0
        total_estimated_cost = logs.aggregate(value=Sum("estimated_cost_usd"))["value"] or 0
        model_usage = list(
            logs.values("selected_provider", "selected_model")
            .annotate(count=Count("id"), estimated_cost_usd=Sum("estimated_cost_usd"))
            .order_by("-count")
        )
        provider_usage = list(
            logs.values("selected_provider")
            .annotate(count=Count("id"), estimated_cost_usd=Sum("estimated_cost_usd"))
            .order_by("-count")
        )
        user_usage = list(
            logs.values("user__username")
            .annotate(count=Count("id"), estimated_cost_usd=Sum("estimated_cost_usd"))
            .order_by("-count")
        )
        policy_usage = list(
            logs.values("policy")
            .annotate(count=Count("id"), estimated_cost_usd=Sum("estimated_cost_usd"))
            .order_by("-count")
        )
        failed_requests = logs.exclude(error_message="").count()
        fallback_attempts = logs.filter(routing_reason__icontains="fallback attempts").count()
        quota_blocks = logs.filter(error_message__icontains="quota").count()
        failure_rate = (failed_requests / total_requests) if total_requests else 0
        provider_health = list(
            logs.values("selected_provider")
            .annotate(
                count=Count("id"),
                failures=Count("id", filter=~Q(error_message="")),
                average_latency_ms=Avg("latency_ms"),
            )
            .order_by("-failures", "-count")
        )
        for item in provider_health:
            item["failure_rate"] = round((item["failures"] / item["count"]) if item["count"] else 0, 4)
            item["average_latency_ms"] = round(item["average_latency_ms"] or 0, 2)
        model_health = list(
            logs.values("selected_provider", "selected_model")
            .annotate(
                count=Count("id"),
                failures=Count("id", filter=~Q(error_message="")),
                average_latency_ms=Avg("latency_ms"),
            )
            .order_by("-failures", "-count")[:10]
        )
        for item in model_health:
            item["failure_rate"] = round((item["failures"] / item["count"]) if item["count"] else 0, 4)
            item["average_latency_ms"] = round(item["average_latency_ms"] or 0, 2)
        recent_errors = list(
            logs.exclude(error_message="")
            .values(
                "id",
                "prompt_summary",
                "selected_provider",
                "selected_model",
                "error_message",
                "created_at",
            )[:5]
        )
        unhealthy_models = []
        for model in LLMModel.objects.filter(is_active=True):
            health_status = evaluate_model_health(provider=model.provider, model_name=model.name, record_event=True)
            if health_status.status == "unhealthy":
                unhealthy_models.append(serialize_model_health_status(health_status))
        recent_health_events = list(
            ModelHealthEvent.objects.values(
                "id",
                "event_type",
                "provider",
                "model_name",
                "status",
                "rule_name",
                "reason",
                "request_count",
                "failures",
                "failure_rate",
                "average_latency_ms",
                "created_at",
            )[:5]
        )
        local_requests = logs.filter(selected_provider="ollama").count()
        local_ratio = (local_requests / total_requests) if total_requests else 0

        return Response(
            {
                "total_requests": total_requests,
                "average_latency_ms": round(average_latency, 2),
                "total_estimated_cost_usd": total_estimated_cost,
                "local_routing_ratio": round(local_ratio, 4),
                "estimated_cost_savings_percent": round(local_ratio * 100, 2),
                "failed_requests": failed_requests,
                "failure_rate": round(failure_rate, 4),
                "fallback_attempts": fallback_attempts,
                "quota_blocks": quota_blocks,
                "filter": active_filter,
                "model_usage": model_usage,
                "provider_usage": provider_usage,
                "user_usage": user_usage,
                "policy_usage": policy_usage,
                "provider_health": provider_health,
                "model_health": model_health,
                "unhealthy_models": unhealthy_models,
                "recent_health_events": recent_health_events,
                "recent_errors": recent_errors,
                "recent_logs": RoutingLogSerializer(logs[:5], many=True).data,
            }
        )
