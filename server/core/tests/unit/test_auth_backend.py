import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from core.auth_backend import EmailBackend


@pytest.mark.unit
class EmailBackendAuthenticateTest(TestCase):

    def setUp(self):
        self.backend = EmailBackend()
        self.request = RequestFactory().get("/")
        self.user = User.objects.create_user(
            username="gabriel",
            email="gabriel@test.com",
            password="password123",
        )

    def test_returns_user_with_valid_email_and_password(self):
        result = self.backend.authenticate(
            self.request, password="password123", email="gabriel@test.com"
        )
        self.assertEqual(result, self.user)

    def test_returns_none_for_nonexistent_email(self):
        result = self.backend.authenticate(
            self.request, password="password123", email="notfound@test.com"
        )
        self.assertIsNone(result)

    def test_returns_none_for_wrong_password(self):
        result = self.backend.authenticate(
            self.request, password="wrongpassword", email="gabriel@test.com"
        )
        self.assertIsNone(result)

    def test_returns_none_without_email_in_kwargs(self):
        result = self.backend.authenticate(
            self.request, username="gabriel", password="password123"
        )
        self.assertIsNone(result)

    def test_returns_none_for_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        result = self.backend.authenticate(
            self.request, password="password123", email="gabriel@test.com"
        )
        self.assertIsNone(result)
