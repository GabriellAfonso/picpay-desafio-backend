from decimal import Decimal
import requests
from django.db import transaction as django_transaction
from features.picpay.exceptions import AuthorizationDenied
from features.picpay.models import PicPayAccount, Transaction
from features.picpay.validators.transaction_validator import TransactionValidator
from features.picpay.repositories.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(self, validator: TransactionValidator, transaction_repo: TransactionRepository):
        self.validator = validator
        self.transaction_repo = transaction_repo

    def process_transaction(self, data: dict) -> Transaction:
        self.validator.validate(data)
        return self._create_transaction(data["value"], data["sender"], data["receiver"])

    def _get_external_authorization(self) -> bool:
        response = requests.get("https://util.devi.tools/api/v2/authorize", timeout=5)
        if response.status_code == 200 and response.json().get("data", {}).get("authorization"):
            return True
        raise AuthorizationDenied

    def _create_transaction(
        self,
        value: Decimal | float | int,
        sender: PicPayAccount,
        receiver: PicPayAccount,
    ) -> Transaction:
        with django_transaction.atomic():
            self._get_external_authorization()
            sender.pay(value)
            receiver.receive(value)
            sender.save()
            receiver.save()
            return self.transaction_repo.create(sender, receiver, value)
