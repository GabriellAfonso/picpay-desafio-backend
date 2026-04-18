from rest_framework import status
from django.utils.translation import gettext_lazy as _


class TransactionExceptions(Exception):
    """Base exception class for transaction-related errors."""

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AccountDoesNotExist(TransactionExceptions):
    """Exception raised when an account does not exist."""

    def __init__(self, account, message=_("Account does not exist!"), status_code=status.HTTP_404_NOT_FOUND):
        self.account = account
        super().__init__(message, status_code)


class SelfTransferError(TransactionExceptions):
    """Exception raised when a transfer to the same account is attempted."""

    def __init__(self, message=_("Transferring to your own account is not allowed"), status_code=status.HTTP_400_BAD_REQUEST):
        super().__init__(message, status_code)


class InsufficientBalanceError(TransactionExceptions):
    """Exception raised when an account has insufficient balance."""

    def __init__(self, sender, message=_("Insufficient balance!"), status_code=status.HTTP_400_BAD_REQUEST):
        self.sender = sender
        super().__init__(message, status_code)


class AuthorizationDenied(TransactionExceptions):
    """Exception raised when authorization is denied."""

    def __init__(self, message=_("Authorization denied, try again"), status_code=status.HTTP_403_FORBIDDEN):
        super().__init__(message, status_code)


class TransferPermissionDenied(TransactionExceptions):
    """Exception raised when transfer permission is denied."""

    def __init__(self, message=_("You do not have permission to make transfers"), status_code=status.HTTP_403_FORBIDDEN):
        super().__init__(message, status_code)


class ReceivePermissionDenied(TransactionExceptions):
    """Exception raised when receive permission is denied."""

    def __init__(self, message=_("You do not have permission to receive transfers"), status_code=status.HTTP_403_FORBIDDEN):
        super().__init__(message, status_code)
