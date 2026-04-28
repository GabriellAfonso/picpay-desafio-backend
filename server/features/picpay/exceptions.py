from rest_framework import status
from django.utils.translation import gettext_lazy as _
from core.exceptions import DomainException


class TransactionExceptions(DomainException):
    """Base exception for picpay transaction-related errors."""


class AccountDoesNotExist(TransactionExceptions):
    """Exception raised when an account does not exist."""

    def __init__(
        self,
        account: object = None,
        message: object = _("Account does not exist!"),
        status_code: int = status.HTTP_404_NOT_FOUND,
    ) -> None:
        self.account = account
        super().__init__(message, status_code)


class SelfTransferError(TransactionExceptions):
    """Exception raised when a transfer to the same account is attempted."""

    def __init__(
        self,
        message: object = _("Transferring to your own account is not allowed"),
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        super().__init__(message, status_code)


class InsufficientBalanceError(TransactionExceptions):
    """Exception raised when an account has insufficient balance."""

    def __init__(
        self,
        sender: object,
        message: object = _("Insufficient balance!"),
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.sender = sender
        super().__init__(message, status_code)


class AuthorizationDenied(TransactionExceptions):
    """Exception raised when authorization is denied."""

    def __init__(
        self,
        message: object = _("Authorization denied, try again"),
        status_code: int = status.HTTP_403_FORBIDDEN,
    ) -> None:
        super().__init__(message, status_code)


class TransferPermissionDenied(TransactionExceptions):
    """Exception raised when transfer permission is denied."""

    def __init__(
        self,
        message: object = _("You do not have permission to make transfers"),
        status_code: int = status.HTTP_403_FORBIDDEN,
    ) -> None:
        super().__init__(message, status_code)


class ReceivePermissionDenied(TransactionExceptions):
    """Exception raised when receive permission is denied."""

    def __init__(
        self,
        message: object = _("You do not have permission to receive transfers"),
        status_code: int = status.HTTP_403_FORBIDDEN,
    ) -> None:
        super().__init__(message, status_code)
