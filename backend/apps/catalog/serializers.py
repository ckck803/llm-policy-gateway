from rest_framework import serializers

from apps.catalog.models import LLMModel, ProviderCredential, RoutingPolicy


class LLMModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMModel
        fields = [
            "id",
            "provider",
            "name",
            "display_name",
            "role",
            "quality_level",
            "speed_level",
            "cost_level",
            "privacy_level",
            "context_window",
            "is_active",
            "created_at",
            "updated_at",
        ]


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


class ProviderCredentialSerializer(serializers.ModelSerializer):
    base_url = serializers.CharField(allow_blank=True, write_only=False)
    access_token = serializers.CharField(allow_blank=True, write_only=False)

    class Meta:
        model = ProviderCredential
        fields = [
            "id",
            "provider",
            "display_name",
            "base_url",
            "access_token",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["base_url"] = instance.get_base_url()
        data["access_token"] = instance.get_access_token()
        return data

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
        if access_token is not None:
            instance.set_access_token(access_token)
        instance.save()
        return instance
