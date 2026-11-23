"""Authentication and user access tests."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
def test_signup_view_success(client):
    """Test user signup and automatic session login."""
    url = reverse("signup")
    response = client.post(
        url,
        {
            "username": "ahmsuser",
            "email": "user@ahms.internal",
            "password1": "SecurePass123!@",
            "password2": "SecurePass123!@",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("dashboard")
    assert User.objects.filter(username="ahmsuser").exists()


@pytest.mark.django_db
def test_login_and_logout_views(client):
    """Test standard login and logout flows."""
    user = User.objects.create_user(
        username="activeuser",
        email="active@ahms.internal",
        password="TestPassword123!",
    )

    # Login
    login_url = reverse("login")
    response = client.post(
        login_url,
        {
            "username": "activeuser",
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("dashboard")

    # Logout
    logout_url = reverse("logout")
    logout_resp = client.post(logout_url)
    assert logout_resp.status_code == 302
    assert logout_resp.url == reverse("login")


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    """Unauthenticated users must be redirected to login."""
    dashboard_url = reverse("dashboard")
    response = client.get(dashboard_url)
    assert response.status_code == 302
    assert reverse("login") in response.url


@pytest.mark.django_db
def test_password_reset_request(client, mailoutbox):
    """Test password reset initiates email dispatch."""
    User.objects.create_user(
        username="resetuser",
        email="reset@ahms.internal",
        password="Password123!",
    )
    reset_url = reverse("password_reset")
    response = client.post(reset_url, {"email": "reset@ahms.internal"})
    assert response.status_code == 302
    assert response.url == reverse("password_reset_done")
    assert len(mailoutbox) == 1
    assert "AHMS Password Reset Request" in mailoutbox[0].subject
