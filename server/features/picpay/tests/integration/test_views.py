import pytest
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from features.picpay.models import PicPayAccount


def make_user(username="john", email="john@test.com", password="password123"):
    return User.objects.create_user(username=username, email=email, password=password)


def make_account(user, document="123.456.789-09"):
    return PicPayAccount.objects.create(
        user=user,
        complete_name="John Doe",
        email=user.email,
        document=document,
        document_type="cpf",
        sex="M",
        account_type="personal",
        balance=Decimal("100.00"),
    )


@pytest.mark.integration
class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("picpay:login")

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_renders_login_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "picpay/login.html")

    @patch("core.forms.authenticate")
    def test_post_valid_credentials_redirects_to_profile(self, mock_authenticate):
        user = make_user()
        user.backend = "core.auth_backend.EmailBackend"
        mock_authenticate.return_value = user
        response = self.client.post(self.url, {
            "email": "john@test.com",
            "password": "password123",
        })
        self.assertRedirects(response, reverse("picpay:profile"), fetch_redirect_response=False)

    def test_post_invalid_credentials_returns_200(self):
        response = self.client.post(self.url, {
            "email": "wrong@test.com",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_credentials_renders_login_template(self):
        response = self.client.post(self.url, {
            "email": "wrong@test.com",
            "password": "wrongpass",
        })
        self.assertTemplateUsed(response, "picpay/login.html")


@pytest.mark.integration
class RegisterViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("picpay:register")

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_renders_register_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "picpay/register.html")

    @patch("features.picpay.views.auth_views.PicPayRegistrationService")
    def test_post_valid_form_redirects_to_login(self, mock_service):
        mock_service.return_value.register.return_value = None
        response = self.client.post(self.url, {
            "complete_name": "John Doe",
            "email": "john@test.com",
            "document": "529.982.247-25",
            "sex": "M",
            "password1": "StrongPass123!",
        })
        self.assertRedirects(response, reverse("picpay:login"), fetch_redirect_response=False)

    def test_post_invalid_form_returns_200(self):
        response = self.client.post(self.url, {
            "complete_name": "",
            "email": "invalid",
            "document": "",
            "sex": "",
            "password1": "",
        })
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_form_renders_register_template(self):
        response = self.client.post(self.url, {
            "complete_name": "",
            "email": "invalid",
        })
        self.assertTemplateUsed(response, "picpay/register.html")


@pytest.mark.integration
class YourProfileViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("picpay:profile")
        self.user = make_user()
        self.account = make_account(self.user)

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"{reverse('picpay:login')}?next={self.url}",
            fetch_redirect_response=False,
        )

    def test_authenticated_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_renders_profile_template(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "picpay/profile.html")


@pytest.mark.integration
class YourProfileContextTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("picpay:profile")
        self.user = make_user()
        self.account = make_account(self.user)
        self.client.force_login(self.user)

    def test_context_contains_display_name(self):
        response = self.client.get(self.url)
        self.assertIn("display_name", response.context)

    def test_context_display_name_is_first_and_last(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["display_name"], "John Doe")

    def test_context_contains_balance(self):
        response = self.client.get(self.url)
        self.assertIn("balance", response.context)

    def test_context_balance_matches_account(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["balance"], Decimal("100.00"))

    def test_context_contains_sex(self):
        response = self.client.get(self.url)
        self.assertIn("sex", response.context)

    def test_context_contains_last_transactions(self):
        response = self.client.get(self.url)
        self.assertIn("last_transactions", response.context)

    def test_context_last_transactions_is_list(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context["last_transactions"], list)


@pytest.mark.integration
class GuestLoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("picpay:guest_login")

    @patch("features.picpay.views.auth_views.GuestLoginService")
    def test_get_redirects_to_profile(self, mock_service_class):
        mock_user = make_user(username="guest_abc", email="guest_abc@guest.local")
        mock_service_class.return_value.create_guest.return_value = mock_user
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("picpay:profile"), fetch_redirect_response=False)

    @patch("features.picpay.views.auth_views.GuestLoginService")
    def test_get_logs_in_the_guest_user(self, mock_service_class):
        mock_user = make_user(username="guest_def", email="guest_def@guest.local")
        make_account(mock_user, document="guest_def")
        mock_service_class.return_value.create_guest.return_value = mock_user
        self.client.get(self.url)
        self.assertIn("_auth_user_id", self.client.session)

    @patch("features.picpay.views.auth_views.GuestLoginService")
    def test_get_calls_create_guest(self, mock_service_class):
        mock_user = make_user(username="guest_ghi", email="guest_ghi@guest.local")
        mock_service_class.return_value.create_guest.return_value = mock_user
        self.client.get(self.url)
        mock_service_class.return_value.create_guest.assert_called_once()


@pytest.mark.integration
class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("picpay:logout")
        self.user = make_user()
        make_account(self.user)

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"{reverse('picpay:login')}?next={self.url}",
            fetch_redirect_response=False,
        )

    def test_authenticated_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("picpay:login"), fetch_redirect_response=False)

    def test_authenticated_user_is_logged_out(self):
        self.client.force_login(self.user)
        self.client.get(self.url)
        response = self.client.get(reverse("picpay:profile"))
        self.assertEqual(response.status_code, 302)
