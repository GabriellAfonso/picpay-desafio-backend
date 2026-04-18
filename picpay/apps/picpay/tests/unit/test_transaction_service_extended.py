import pytest
from decimal import Decimal
from django.test import TestCase
from unittest.mock import patch, Mock, call
from apps.picpay.exceptions import AuthorizationDenied
from apps.picpay.services.transaction_service import TransactionService


def make_mock_account(account_id, balance=100):
    account = Mock()
    account.id = account_id
    account.balance = balance
    return account


def make_service():
    return TransactionService(validator=Mock(), transaction_model=Mock())


def make_authorized_response():
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"data": {"authorization": True}}
    return response


def make_unauthorized_response():
    response = Mock()
    response.status_code = 403
    response.json.return_value = {}
    return response


@pytest.mark.unit
class GetExternalAuthorizationTest(TestCase):

    @patch("apps.picpay.services.transaction_service.requests")
    def test_returns_true_when_authorized(self, mock_requests):
        mock_requests.get.return_value = make_authorized_response()
        service = make_service()
        result = service._get_external_authorization()
        self.assertTrue(result)

    @patch("apps.picpay.services.transaction_service.requests")
    def test_raises_authorization_denied_when_status_is_not_200(self, mock_requests):
        mock_requests.get.return_value = make_unauthorized_response()
        service = make_service()
        with self.assertRaises(AuthorizationDenied):
            service._get_external_authorization()

    @patch("apps.picpay.services.transaction_service.requests")
    def test_raises_authorization_denied_when_authorization_is_false(self, mock_requests):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"data": {"authorization": False}}
        mock_requests.get.return_value = response
        service = make_service()
        with self.assertRaises(AuthorizationDenied):
            service._get_external_authorization()

    @patch("apps.picpay.services.transaction_service.requests")
    def test_calls_correct_external_url(self, mock_requests):
        mock_requests.get.return_value = make_authorized_response()
        service = make_service()
        service._get_external_authorization()
        mock_requests.get.assert_called_once_with("https://util.devi.tools/api/v2/authorize")


@pytest.mark.unit
class CreateTransactionTest(TestCase):

    @patch("apps.picpay.services.transaction_service.requests")
    def test_calls_pay_on_sender(self, mock_requests):
        mock_requests.get.return_value = make_authorized_response()
        service = make_service()
        sender = make_mock_account(1)
        receiver = make_mock_account(2)
        service._create_transaction(Decimal("50.00"), sender, receiver)
        sender.pay.assert_called_once_with(Decimal("50.00"))

    @patch("apps.picpay.services.transaction_service.requests")
    def test_calls_receive_on_receiver(self, mock_requests):
        mock_requests.get.return_value = make_authorized_response()
        service = make_service()
        sender = make_mock_account(1)
        receiver = make_mock_account(2)
        service._create_transaction(Decimal("50.00"), sender, receiver)
        receiver.receive.assert_called_once_with(Decimal("50.00"))

    @patch("apps.picpay.services.transaction_service.requests")
    def test_saves_sender_and_receiver(self, mock_requests):
        mock_requests.get.return_value = make_authorized_response()
        service = make_service()
        sender = make_mock_account(1)
        receiver = make_mock_account(2)
        service._create_transaction(Decimal("50.00"), sender, receiver)
        sender.save.assert_called_once()
        receiver.save.assert_called_once()

    @patch("apps.picpay.services.transaction_service.requests")
    def test_does_not_pay_or_save_when_authorization_denied(self, mock_requests):
        mock_requests.get.return_value = make_unauthorized_response()
        service = make_service()
        sender = make_mock_account(1)
        receiver = make_mock_account(2)
        with self.assertRaises(AuthorizationDenied):
            service._create_transaction(Decimal("50.00"), sender, receiver)
        sender.pay.assert_not_called()
        receiver.receive.assert_not_called()
        sender.save.assert_not_called()
        receiver.save.assert_not_called()
