from django.db.models import Avg, Count
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasScreenAccess
from apps.logs.models import RoutingLog
from apps.logs.serializers import RoutingLogSerializer


class DashboardMetricsView(APIView):
    permission_classes = [HasScreenAccess]
    required_screen = "dashboard"

    def get(self, request):
        logs = RoutingLog.objects.all()
        total_requests = logs.count()
        average_latency = logs.aggregate(value=Avg("latency_ms"))["value"] or 0
        model_usage = list(
            logs.values("selected_provider", "selected_model")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        policy_usage = list(
            logs.values("policy").annotate(count=Count("id")).order_by("-count")
        )
        local_requests = logs.filter(selected_provider="ollama").count()
        local_ratio = (local_requests / total_requests) if total_requests else 0

        return Response(
            {
                "total_requests": total_requests,
                "average_latency_ms": round(average_latency, 2),
                "local_routing_ratio": round(local_ratio, 4),
                "estimated_cost_savings_percent": round(local_ratio * 100, 2),
                "model_usage": model_usage,
                "policy_usage": policy_usage,
                "recent_logs": RoutingLogSerializer(logs[:5], many=True).data,
            }
        )
