import pytest
from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from apps.picpay.models import PicPayAccount
from apps.picpay.services.register_picpay_user import PicPayRegistrationService


def make_form_data(document_type="cpf", document="123.456.789-09"):
    return {
        "email": "john@test.com",
        "password1": "StrongPass123!",
        "complete_name": "John Doe",
        "document": document,
        "document_type": document_type,
        "sex": "M",
    }


@pytest.mark.unit
class GetAccountTypeTest(TestCase):

    def test_returns_personal_for_cpf(self):
        service = PicPayRegistrationService(form=make_form_data(document_type="cpf"))
        self.assertEqual(service._get_account_type(), "personal")

    def test_returns_merchant_for_cnpj(self):
        service = PicPayRegistrationService(form=make_form_data(document_type="cnpj"))
        self.assertEqual(service._get_account_type(), "merchant")


@pytest.mark.unit
class RegisterTest(TestCase):

    @patch("apps.picpay.services.register_picpay_user.assign_role")
    def test_creates_user_with_email_as_username(self, mock_assign_role):
        service = PicPayRegistrationService(form=make_form_data())
        service.register()
        user = User.objects.get(email="john@test.com")
        self.assertEqual(user.username, "john@test.com")

    @patch("apps.picpay.services.register_picpay_user.assign_role")
    def test_creates_picpay_account(self, mock_assign_role):
        service = PicPayRegistrationService(form=make_form_data())
        service.register()
        self.assertTrue(PicPayAccount.objects.filter(document="123.456.789-09").exists())

    @patch("apps.picpay.services.register_picpay_user.assign_role")
    def test_assigns_personal_role_for_cpf(self, mock_assign_role):
        service = PicPayRegistrationService(form=make_form_data(document_type="cpf"))
        service.register()
        user = User.objects.get(email="john@test.com")
        mock_assign_role.assert_called_once_with(user, "personal")

    @patch("apps.picpay.services.register_picpay_user.assign_role")
    def test_assigns_merchant_role_for_cnpj(self, mock_assign_role):
        data = make_form_data(document_type="cnpj", document="12.345.678/0001-90")
        service = PicPayRegistrationService(form=data)
        service.register()
        user = User.objects.get(email="john@test.com")
        mock_assign_role.assert_called_once_with(user, "merchant")

    @patch("apps.picpay.services.register_picpay_user.assign_role")
    def test_account_initial_balance_is_100(self, mock_assign_role):
        service = PicPayRegistrationService(form=make_form_data())
        service.register()
        account = PicPayAccount.objects.get(document="123.456.789-09")
        self.assertEqual(account.balance, 100)

    @patch("apps.picpay.services.register_picpay_user.assign_role")
    def test_rollback_on_failure(self, mock_assign_role):
        mock_assign_role.side_effect = Exception("role assignment failed")
        service = PicPayRegistrationService(form=make_form_data())
        with self.assertRaises(Exception):
            service.register()
        self.assertFalse(User.objects.filter(email="john@test.com").exists())
