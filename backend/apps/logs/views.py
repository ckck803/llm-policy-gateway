from rest_framework import generics

from apps.accounts.permissions import HasScreenAccess
from apps.logs.models import RoutingLog
from apps.logs.serializers import RoutingLogSerializer


class RoutingLogListView(generics.ListAPIView):
    queryset = RoutingLog.objects.all()[:100]
    serializer_class = RoutingLogSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "logs"
