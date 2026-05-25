from rest_framework import generics

from apps.accounts.permissions import HasScreenAccess
from apps.catalog.models import LLMModel, ProviderCredential, RoutingPolicy
from apps.catalog.serializers import LLMModelSerializer, ProviderCredentialSerializer, RoutingPolicySerializer


class LLMModelListView(generics.ListCreateAPIView):
    queryset = LLMModel.objects.all()
    serializer_class = LLMModelSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "models"


class LLMModelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LLMModel.objects.all()
    serializer_class = LLMModelSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "models"


class PolicyListView(generics.ListCreateAPIView):
    queryset = RoutingPolicy.objects.all()
    serializer_class = RoutingPolicySerializer
    permission_classes = [HasScreenAccess]
    required_screen = "policies"


class PolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoutingPolicy.objects.all()
    serializer_class = RoutingPolicySerializer
    permission_classes = [HasScreenAccess]
    required_screen = "policies"


class ProviderCredentialListView(generics.ListCreateAPIView):
    queryset = ProviderCredential.objects.all()
    serializer_class = ProviderCredentialSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "credentials"


class ProviderCredentialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProviderCredential.objects.all()
    serializer_class = ProviderCredentialSerializer
    permission_classes = [HasScreenAccess]
    required_screen = "credentials"
