import pytest
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from features.picpay.models import PicPayAccount, Transaction
from features.picpay.exceptions import InsufficientBalanceError


def make_user(username="john", email="john@test.com"):
    return User.objects.create_user(username=username, email=email, password="password123")


def make_account(user, document="123.456.789-09"):
    return PicPayAccount.objects.create(
        user=user,
        complete_name="John Doe",
        email=user.email,
        document=document,
        document_type="cpf",
        sex="M",
        account_type="personal",
        balance=Decimal("200.00"),
    )


@pytest.mark.integration
class TransactionAPIViewGetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("picpay:api_transaction")
        self.user = make_user()
        make_account(self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


@pytest.mark.integration
class TransactionAPIViewPostTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("picpay:api_transaction")
        self.sender_user = make_user("sender", "sender@test.com")
        self.receiver_user = make_user("receiver", "receiver@test.com")
        self.sender = make_account(self.sender_user, "529.982.247-25")
        self.receiver = make_account(self.receiver_user, "111.444.777-35")
        self.client.force_authenticate(user=self.sender_user)

    @patch("features.picpay.views.api_views.TransactionService")
    def test_post_valid_transaction_returns_201(self, mock_service):
        real_transaction = Transaction.objects.create(
            value=Decimal("50.00"),
            sender=self.sender,
            receiver=self.receiver,
        )
        mock_service.return_value.process_transaction.return_value = real_transaction

        response = self.client.post(self.url, {
            "value": "50,00",
            "document": self.receiver.document,
        }, enforce_csrf_checks=False)

        self.assertEqual(response.status_code, 201)

    @patch("features.picpay.views.api_views.TransactionService")
    def test_post_transaction_exception_returns_correct_status(self, mock_service):
        mock_service.return_value.process_transaction.side_effect = InsufficientBalanceError(
            sender=self.sender
        )
        response = self.client.post(self.url, {
            "value": "9999,00",
            "document": self.receiver.document,
        }, enforce_csrf_checks=False)
        self.assertEqual(response.status_code, 400)

    def test_post_with_nonexistent_receiver_returns_404(self):
        response = self.client.post(self.url, {
            "value": "50,00",
            "document": "000.000.000-00",
        }, enforce_csrf_checks=False)
        self.assertEqual(response.status_code, 404)


@pytest.mark.integration
class TransactionAPIViewParseValueTest(TestCase):

    def setUp(self):
        from features.picpay.views.api_views import TransactionAPIView
        self.view = TransactionAPIView()

    def test_parses_integer_string(self):
        self.assertEqual(self.view._parse_value("50"), 50.0)

    def test_dot_is_treated_as_thousands_separator(self):
        # In BR format, dot = thousands separator: "50.00" means 5000
        self.assertEqual(self.view._parse_value("50.00"), 5000.0)

    def test_parses_decimal_with_comma(self):
        self.assertEqual(self.view._parse_value("50,00"), 50.0)

    def test_parses_value_with_dot_as_thousands_separator(self):
        self.assertAlmostEqual(self.view._parse_value("1.000,50"), 1000.50)

    def test_parses_large_value(self):
        self.assertEqual(self.view._parse_value("9999,99"), 9999.99)

    def test_raises_on_non_numeric_string(self):
        with self.assertRaises((ValueError, AttributeError)):
            self.view._parse_value("abc")


@pytest.mark.integration
class RecipientPreviewAPIViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("picpay:recipient_preview")
        self.user = make_user()
        self.account = make_account(self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_with_valid_document_returns_200(self):
        response = self.client.get(self.url, {"document": self.account.document})
        self.assertEqual(response.status_code, 200)

    def test_get_with_valid_document_returns_complete_name(self):
        response = self.client.get(self.url, {"document": self.account.document})
        self.assertIn("complete_name", response.data)

    def test_get_without_document_returns_400(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_get_with_nonexistent_document_returns_404(self):
        response = self.client.get(self.url, {"document": "000.000.000-00"})
        self.assertEqual(response.status_code, 404)
