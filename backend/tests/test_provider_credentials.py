import pytest

from apps.catalog.crypto import decrypt_value, encrypt_value
from apps.catalog.credentials import get_provider_access_token, get_provider_base_url
from apps.catalog.models import ProviderCredential
from apps.catalog.serializers import ProviderCredentialSerializer


@pytest.mark.django_db
def test_provider_credential_encrypts_url_and_token_in_database():
    credential = ProviderCredential.objects.create(
        provider="openai",
        display_name="OpenAI Production",
    )
    credential.set_base_url("https://api.openai.com/v1")
    credential.set_access_token("sk-test-token")
    credential.save()

    stored = ProviderCredential.objects.get(id=credential.id)

    assert stored.encrypted_base_url != "https://api.openai.com/v1"
    assert stored.encrypted_access_token != "sk-test-token"
    assert stored.get_base_url() == "https://api.openai.com/v1"
    assert stored.get_access_token() == "sk-test-token"


def test_encrypt_value_round_trips_plaintext():
    encrypted = encrypt_value("secret")

    assert encrypted != "secret"
    assert decrypt_value(encrypted) == "secret"


@pytest.mark.django_db
def test_provider_credential_lookup_prefers_active_database_value():
    credential = ProviderCredential.objects.create(
        provider="openai",
        display_name="OpenAI Production",
        is_active=True,
    )
    credential.set_base_url("https://stored.example/v1")
    credential.set_access_token("stored-token")
    credential.save()

    assert get_provider_base_url("openai", "https://fallback.example/v1") == "https://stored.example/v1"
    assert get_provider_access_token("openai", "fallback-token") == "stored-token"


@pytest.mark.django_db
def test_provider_credential_serializer_reads_and_updates_decrypted_fields():
    credential = ProviderCredential.objects.create(
        provider="gemini",
        display_name="Gemini Dev",
    )
    credential.set_base_url("https://generativelanguage.googleapis.com/v1beta")
    credential.set_access_token("gemini-token")
    credential.save()

    assert ProviderCredentialSerializer(credential).data["base_url"] == (
        "https://generativelanguage.googleapis.com/v1beta"
    )
    assert ProviderCredentialSerializer(credential).data["access_token"] == "gemini-token"

    serializer = ProviderCredentialSerializer(
        credential,
        data={
            "provider": "gemini",
            "display_name": "Gemini Updated",
            "base_url": "https://example.test/gemini",
            "access_token": "new-token",
            "is_active": True,
        },
    )
    assert serializer.is_valid(), serializer.errors
    serializer.save()
    credential.refresh_from_db()

    assert credential.display_name == "Gemini Updated"
    assert credential.encrypted_base_url != "https://example.test/gemini"
    assert credential.encrypted_access_token != "new-token"
    assert credential.get_base_url() == "https://example.test/gemini"
    assert credential.get_access_token() == "new-token"
