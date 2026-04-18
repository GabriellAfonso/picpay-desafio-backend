import pytest
from django.test import TestCase
from unittest.mock import patch, Mock
from apps.picpay.exceptions import AuthorizationDenied
from apps.picpay.services.transaction_service import TransactionService


@pytest.mark.unit
class TransactionServiceTest(TestCase):

    def setUp(self):
        self.service = TransactionService(
            validator=Mock(), transaction_model=Mock)

        self.sender = Mock()
        self.sender.id = 1
        self.sender.balance = 100

        self.receiver = Mock()
        self.receiver.id = 2

        self.data = {
            'sender': self.sender,
            'receiver': self.receiver,
            'value': 50,
        }

    def mock_response(self, status_code=200, json_data=None):
        response = Mock()
        response.status_code = status_code
        response.json.return_value = json_data or {}
        return response

    @patch('apps.picpay.services.transaction_service.requests')
    def test_process_transaction_success(self, mock_requests):

        mock_requests.get.return_value = self.mock_response(
            200, {'data': {'authorization': True}})

        self.service.process_transaction(self.data)

    @patch('apps.picpay.services.transaction_service.requests')
    def test_process_transaction_raises_authorization_denied(self, mock_requests):

        mock_requests.get.return_value = self.mock_response(403, {})

        with self.assertRaises(AuthorizationDenied):
            self.service.process_transaction(self.data)

        self.sender.pay.assert_not_called()
        self.receiver.receive.assert_not_called()
        self.sender.save.assert_not_called()
        self.receiver.save.assert_not_called()
