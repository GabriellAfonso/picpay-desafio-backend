from django.db import transaction
from rolepermissions.roles import assign_role
from features.picpay.repositories.account_repository import AccountRepository


class PicPayRegistrationService:

    def __init__(self, form: dict, account_repo: AccountRepository):
        self.form_data = form
        self.account_repo = account_repo

    def _get_account_type(self) -> str:
        if self.form_data['document_type'] == 'cpf':
            return 'personal'
        return 'merchant'

    def register(self):
        with transaction.atomic():
            user = self.account_repo.create_user(
                email=self.form_data['email'],
                password=self.form_data['password1'],
            )
            account_type = self._get_account_type()
            assign_role(user, account_type)
            self.account_repo.create_account(user, {**self.form_data, 'account_type': account_type})
