import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from core.forms import BaseRegisterForm, EmailAuthenticationForm


def valid_base_form_data(username="johndoe", email="john@test.com"):
    return {
        "username": username,
        "email": email,
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    }


@pytest.mark.unit
class BaseRegisterFormTest(TestCase):

    def test_valid_data_is_valid(self):
        form = BaseRegisterForm(data=valid_base_form_data())
        self.assertTrue(form.is_valid())

    def test_username_too_short_is_invalid(self):
        data = valid_base_form_data(username="ab")
        form = BaseRegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_username_required(self):
        data = valid_base_form_data(username="")
        form = BaseRegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_password_mismatch_is_invalid(self):
        data = valid_base_form_data()
        data["password2"] = "DifferentPass456!"
        form = BaseRegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_duplicate_email_is_invalid(self):
        User.objects.create_user(username="existing", email="john@test.com", password="password123")
        form = BaseRegisterForm(data=valid_base_form_data(username="newuser", email="john@test.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_email_not_required(self):
        data = valid_base_form_data()
        data["email"] = ""
        form = BaseRegisterForm(data=data)
        self.assertTrue(form.is_valid())


@pytest.mark.unit
class EmailAuthenticationFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="john",
            email="john@test.com",
            password="password123",
        )

    @patch("core.forms.authenticate")
    def test_valid_credentials_are_valid(self, mock_authenticate):
        mock_authenticate.return_value = self.user
        form = EmailAuthenticationForm(data={"email": "john@test.com", "password": "password123"})
        self.assertTrue(form.is_valid())

    @patch("core.forms.authenticate")
    def test_invalid_credentials_raise_validation_error(self, mock_authenticate):
        mock_authenticate.return_value = None
        form = EmailAuthenticationForm(data={"email": "john@test.com", "password": "wrongpass"})
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_missing_email_is_invalid(self):
        form = EmailAuthenticationForm(data={"email": "", "password": "password123"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_missing_password_is_invalid(self):
        form = EmailAuthenticationForm(data={"email": "john@test.com", "password": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    @patch("core.forms.authenticate")
    def test_get_user_returns_authenticated_user(self, mock_authenticate):
        mock_authenticate.return_value = self.user
        form = EmailAuthenticationForm(data={"email": "john@test.com", "password": "password123"})
        form.is_valid()
        self.assertEqual(form.get_user(), self.user)
