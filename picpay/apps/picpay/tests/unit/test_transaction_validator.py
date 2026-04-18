import pytest
from django.test import TestCase
from unittest.mock import Mock, patch
from apps.picpay.validators.transaction_validator import TransactionValidator
from apps.picpay.exceptions import (
    SelfTransferError, InsufficientBalanceError,
    TransferPermissionDenied, ReceivePermissionDenied
)
from django.core.exceptions import ValidationError


@pytest.mark.unit
class TransactionValidatorTest(TestCase):

    def setUp(self):
        self.validator = TransactionValidator()

        self.sender = Mock()
        self.sender.id = 1
        self.sender.balance = 100
        self.sender.user = Mock()

        self.receiver = Mock()
        self.receiver.id = 2
        self.receiver.user = Mock()

    @patch('apps.picpay.validators.transaction_validator.has_permission')
    def test_validate_success(self, mock_has_permission):
        mock_has_permission.side_effect = [True, True]
        data = {'sender': self.sender, 'receiver': self.receiver, 'value': 50}
        # Não deve levantar exceção
        self.validator.validate(data)

    @patch('apps.picpay.validators.transaction_validator.has_permission')
    def test_validate_negative_value(self, mock_has_permission):
        mock_has_permission.side_effect = [True, True]
        data = {'sender': self.sender, 'receiver': self.receiver, 'value': 0}
        with self.assertRaises(ValidationError):
            self.validator.validate(data)

    @patch('apps.picpay.validators.transaction_validator.has_permission')
    def test_validate_self_transfer(self, mock_has_permission):
        mock_has_permission.side_effect = [True, True]
        data = {'sender': self.sender, 'receiver': self.sender, 'value': 10}
        with self.assertRaises(SelfTransferError):
            self.validator.validate(data)

    @patch('apps.picpay.validators.transaction_validator.has_permission')
    def test_validate_insufficient_balance(self, mock_has_permission):
        mock_has_permission.side_effect = [True, True]
        self.sender.balance = 10
        data = {'sender': self.sender, 'receiver': self.receiver, 'value': 20}
        with self.assertRaises(InsufficientBalanceError):
            self.validator.validate(data)

    @patch('apps.picpay.validators.transaction_validator.has_permission')
    def test_validate_sender_no_permission(self, mock_has_permission):
        mock_has_permission.side_effect = [False, True]
        data = {'sender': self.sender, 'receiver': self.receiver, 'value': 10}
        with self.assertRaises(TransferPermissionDenied):
            self.validator.validate(data)

    @patch('apps.picpay.validators.transaction_validator.has_permission')
    def test_validate_receiver_no_permission(self, mock_has_permission):
        mock_has_permission.side_effect = [True, False]
        data = {'sender': self.sender, 'receiver': self.receiver, 'value': 10}
        with self.assertRaises(ReceivePermissionDenied):
            self.validator.validate(data)
