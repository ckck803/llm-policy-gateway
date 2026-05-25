from django.contrib import admin
from django.urls import path

from apps.accounts.views import LoginView, LogoutView, MeView, ScreenDetailView, ScreenListView, UserDetailView, UserListView
from apps.catalog.views import (
    LLMModelDetailView,
    LLMModelListView,
    PolicyDetailView,
    PolicyListView,
    ProviderCredentialDetailView,
    ProviderCredentialListView,
)
from apps.dashboard.views import DashboardMetricsView
from apps.logs.views import RoutingLogListView
from apps.routing.views import ChatView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/me/", MeView.as_view(), name="me"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/users/", UserListView.as_view(), name="users"),
    path("api/users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("api/screens/", ScreenListView.as_view(), name="screens"),
    path("api/screens/<int:pk>/", ScreenDetailView.as_view(), name="screen-detail"),
    path("api/chat/", ChatView.as_view(), name="chat"),
    path("api/models/", LLMModelListView.as_view(), name="models"),
    path("api/models/<int:pk>/", LLMModelDetailView.as_view(), name="model-detail"),
    path("api/policies/", PolicyListView.as_view(), name="policies"),
    path("api/policies/<int:pk>/", PolicyDetailView.as_view(), name="policy-detail"),
    path("api/provider-credentials/", ProviderCredentialListView.as_view(), name="provider-credentials"),
    path("api/provider-credentials/<int:pk>/", ProviderCredentialDetailView.as_view(), name="provider-credential-detail"),
    path("api/routing-logs/", RoutingLogListView.as_view(), name="routing-logs"),
    path("api/dashboard/metrics/", DashboardMetricsView.as_view(), name="dashboard-metrics"),
]
