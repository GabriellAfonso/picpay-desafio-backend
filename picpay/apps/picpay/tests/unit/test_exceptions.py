import pytest
from django.test import TestCase
from rest_framework import status
from apps.picpay.exceptions import (
    TransactionExceptions,
    AccountDoesNotExist,
    SelfTransferError,
    InsufficientBalanceError,
    AuthorizationDenied,
    TransferPermissionDenied,
    ReceivePermissionDenied,
)


@pytest.mark.unit
class TransactionExceptionsTest(TestCase):

    def test_base_exception_stores_message_and_status_code(self):
        exc = TransactionExceptions("error", status.HTTP_400_BAD_REQUEST)
        self.assertEqual(exc.message, "error")
        self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)

    def test_base_exception_is_instance_of_exception(self):
        exc = TransactionExceptions("error", status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(exc, Exception)


@pytest.mark.unit
class AccountDoesNotExistTest(TestCase):

    def test_default_status_code_is_404(self):
        exc = AccountDoesNotExist(account="user123")
        self.assertEqual(exc.status_code, status.HTTP_404_NOT_FOUND)

    def test_stores_account(self):
        exc = AccountDoesNotExist(account="user123")
        self.assertEqual(exc.account, "user123")

    def test_is_subclass_of_transaction_exceptions(self):
        exc = AccountDoesNotExist(account="user123")
        self.assertIsInstance(exc, TransactionExceptions)


@pytest.mark.unit
class SelfTransferErrorTest(TestCase):

    def test_default_status_code_is_400(self):
        exc = SelfTransferError()
        self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)

    def test_is_subclass_of_transaction_exceptions(self):
        exc = SelfTransferError()
        self.assertIsInstance(exc, TransactionExceptions)


@pytest.mark.unit
class InsufficientBalanceErrorTest(TestCase):

    def test_default_status_code_is_400(self):
        exc = InsufficientBalanceError(sender="sender123")
        self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stores_sender(self):
        exc = InsufficientBalanceError(sender="sender123")
        self.assertEqual(exc.sender, "sender123")

    def test_is_subclass_of_transaction_exceptions(self):
        exc = InsufficientBalanceError(sender="sender123")
        self.assertIsInstance(exc, TransactionExceptions)


@pytest.mark.unit
class AuthorizationDeniedTest(TestCase):

    def test_default_status_code_is_403(self):
        exc = AuthorizationDenied()
        self.assertEqual(exc.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_subclass_of_transaction_exceptions(self):
        exc = AuthorizationDenied()
        self.assertIsInstance(exc, TransactionExceptions)


@pytest.mark.unit
class TransferPermissionDeniedTest(TestCase):

    def test_default_status_code_is_403(self):
        exc = TransferPermissionDenied()
        self.assertEqual(exc.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_subclass_of_transaction_exceptions(self):
        exc = TransferPermissionDenied()
        self.assertIsInstance(exc, TransactionExceptions)


@pytest.mark.unit
class ReceivePermissionDeniedTest(TestCase):

    def test_default_status_code_is_403(self):
        exc = ReceivePermissionDenied()
        self.assertEqual(exc.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_subclass_of_transaction_exceptions(self):
        exc = ReceivePermissionDenied()
        self.assertIsInstance(exc, TransactionExceptions)
