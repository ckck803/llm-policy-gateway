import pytest
from django.contrib.auth.models import User
from django.contrib.auth.hashers import identify_hasher
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.accounts.models import UserScreenAccess


@pytest.mark.django_db
def test_login_returns_token_and_allowed_screens():
    user = User.objects.create_user(username="operator", password="pass12345")
    UserScreenAccess.objects.create(user=user, allowed_screens=["dashboard", "playground"])

    response = APIClient().post(
        "/api/auth/login/",
        {"username": "operator", "password": "pass12345"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["token"]
    assert response.data["user"]["username"] == "operator"
    assert response.data["user"]["allowed_screens"] == ["dashboard", "playground"]


@pytest.mark.django_db
def test_new_passwords_are_stored_with_bcrypt_sha256():
    user = User.objects.create_user(username="bcrypt-user", password="pass12345")

    assert user.password.startswith("bcrypt_sha256$")
    assert identify_hasher(user.password).algorithm == "bcrypt_sha256"
    assert user.check_password("pass12345")


@pytest.mark.django_db
def test_protected_api_requires_authentication():
    response = APIClient().get("/api/models/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_users_api_requires_staff_user():
    normal_user = User.objects.create_user(username="viewer", password="pass12345")
    Token.objects.create(user=normal_user)
    staff_user = User.objects.create_user(username="admin", password="pass12345", is_staff=True)
    Token.objects.create(user=staff_user)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {normal_user.auth_token.key}")
    assert client.get("/api/users/").status_code == 403

    client.credentials(HTTP_AUTHORIZATION=f"Token {staff_user.auth_token.key}")
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert any(user["username"] == "viewer" for user in response.data)


@pytest.mark.django_db
def test_staff_can_create_user_with_screen_access():
    staff_user = User.objects.create_user(username="admin", password="pass12345", is_staff=True)
    Token.objects.create(user=staff_user)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {staff_user.auth_token.key}")
    response = client.post(
        "/api/users/",
        {
            "username": "analyst",
            "password": "pass12345",
            "is_staff": False,
            "is_active": True,
            "allowed_screens": ["dashboard", "logs"],
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["allowed_screens"] == ["dashboard", "logs"]
    created = User.objects.get(username="analyst")
    assert created.password.startswith("bcrypt_sha256$")
    assert created.screen_access.allowed_screens == ["dashboard", "logs"]


@pytest.mark.django_db
def test_staff_can_manage_dynamic_screen_ids():
    staff_user = User.objects.create_user(username="admin", password="pass12345", is_staff=True)
    Token.objects.create(user=staff_user)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {staff_user.auth_token.key}")
    response = client.post(
        "/api/users/",
        {
            "username": "custom-access",
            "password": "pass12345",
            "is_staff": False,
            "is_active": True,
            "allowed_screens": ["dashboard", "reports", "reports", "  audit  "],
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["allowed_screens"] == ["dashboard", "reports", "audit"]


@pytest.mark.django_db
def test_staff_can_fetch_available_screens():
    staff_user = User.objects.create_user(username="admin", password="pass12345", is_staff=True)
    Token.objects.create(user=staff_user)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {staff_user.auth_token.key}")
    response = client.get("/api/screens/")

    assert response.status_code == 200
    assert any(screen["id"] == "dashboard" and screen["label"] == "Dashboard" for screen in response.data)


@pytest.mark.django_db
def test_staff_can_crud_screen_definitions():
    staff_user = User.objects.create_user(username="admin", password="pass12345", is_staff=True)
    Token.objects.create(user=staff_user)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {staff_user.auth_token.key}")
    create_response = client.post(
        "/api/screens/",
        {
            "id": "reports",
            "label": "Reports",
            "description": "Report dashboard",
            "sort_order": 120,
            "is_active": True,
        },
        format="json",
    )

    assert create_response.status_code == 201
    assert create_response.data["id"] == "reports"

    update_response = client.patch(
        f"/api/screens/{create_response.data['pk']}/",
        {"label": "Analytics Reports", "is_active": False},
        format="json",
    )

    assert update_response.status_code == 200
    assert update_response.data["label"] == "Analytics Reports"
    assert update_response.data["is_active"] is False

    delete_response = client.delete(f"/api/screens/{create_response.data['pk']}/")
    assert delete_response.status_code == 204


@pytest.mark.django_db
def test_screen_access_is_enforced_on_backend_api():
    user = User.objects.create_user(username="limited", password="pass12345")
    UserScreenAccess.objects.create(user=user, allowed_screens=["dashboard"])
    Token.objects.create(user=user)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {user.auth_token.key}")

    assert client.get("/api/dashboard/metrics/").status_code == 200
    assert client.get("/api/provider-credentials/").status_code == 403
