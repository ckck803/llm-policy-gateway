from django.contrib import admin

from apps.catalog.models import LLMModel, RoutingPolicy


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    list_display = ("provider", "name", "role", "privacy_level", "is_active")
    list_filter = ("provider", "role", "privacy_level", "is_active")
    search_fields = ("name", "display_name")


@admin.register(RoutingPolicy)
class RoutingPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "display_name", "is_active")
    search_fields = ("name", "display_name")
