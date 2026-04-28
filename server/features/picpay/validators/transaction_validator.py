from decimal import Decimal
from rolepermissions.checkers import has_permission
from features.picpay.exceptions import (
    SelfTransferError,
    InsufficientBalanceError,
    TransferPermissionDenied,
    ReceivePermissionDenied,
)
from features.picpay.models import PicPayAccount
from django.core.exceptions import ValidationError


class TransactionValidator:
    def validate(self, data: dict) -> None:
        sender: PicPayAccount = data["sender"]
        receiver: PicPayAccount = data["receiver"]
        self._check_positive_value(data["value"])
        self._check_not_self_transfer(sender, receiver)
        self._check_balance_sufficient(sender, data["value"])
        self._check_permissions(sender, receiver)

    def _check_positive_value(self, value: Decimal | float | int) -> None:
        if value <= 0:
            raise ValidationError("O valor da transação deve ser positivo.")

    def _check_not_self_transfer(
        self, sender: PicPayAccount, receiver: PicPayAccount
    ) -> None:
        if sender.id == receiver.id:
            raise SelfTransferError

    def _check_balance_sufficient(
        self, sender: PicPayAccount, value: Decimal | float | int
    ) -> None:
        if sender.balance < value:
            raise InsufficientBalanceError(sender)

    def _check_permissions(
        self, sender: PicPayAccount, receiver: PicPayAccount
    ) -> None:
        if not has_permission(sender.user, "make_transfer"):
            raise TransferPermissionDenied
        elif not has_permission(receiver.user, "receive_transfer"):
            raise ReceivePermissionDenied
