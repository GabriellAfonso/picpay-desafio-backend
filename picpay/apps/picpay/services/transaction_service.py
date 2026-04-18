import requests
from apps.picpay.exceptions import AuthorizationDenied
from django.db import transaction as django_transaction
from apps.picpay.validators.transaction_validator import TransactionValidator
from apps.picpay.models import Transaction


class TransactionService():
    def __init__(self, validator: TransactionValidator, transaction_model: Transaction):
        self.validator = validator
        self.transaction_model = transaction_model

    def process_transaction(self, data):
        self.validator.validate(data)
        return self._create_transaction(data['value'], data['sender'], data['receiver'])

    def _get_external_authorization(self):
        external_service_url = 'https://util.devi.tools/api/v2/authorize'

        response = requests.get(external_service_url)
        response_data = response.json()
        if response.status_code == 200 and response_data.get('data', {}).get('authorization'):
            return True
        raise AuthorizationDenied

    def _create_transaction(self, value, sender, receiver):
        transaction_value = value
        with django_transaction.atomic():
            self._get_external_authorization()
            sender.pay(transaction_value)
            receiver.receive(transaction_value)

            transaction_db = self.transaction_model(
                sender=sender,
                receiver=receiver,
                value=transaction_value,
            )

            sender.save()
            receiver.save()
            transaction_db.save()
            return transaction_db
