from django.db import transaction
from rolepermissions.roles import assign_role
from django.contrib.auth.models import User
from apps.picpay.models import PicPayAccount


class PicPayRegistrationService():

    def __init__(self, form: dict):
        self.form_data = form

    def _get_account_type(self):
        doc = self.form_data['document']
        doc_type = self.form_data['document_type']
        if doc_type == 'cpf':
            return 'personal'
        return 'merchant'

    def register(self):
        """Registra o usuário e a conta PicPay no banco de dados."""
        with transaction.atomic():
            user = User(
                email=self.form_data['email'],
                username=self.form_data['email'],
            )
            user.set_password(self.form_data['password1'])
            user.save()

            assign_role(user, self._get_account_type())

            account = PicPayAccount(
                user=user,
                complete_name=self.form_data['complete_name'],
                document=self.form_data['document'],
                document_type=self.form_data['document_type'],
                sex=self.form_data['sex'],
                account_type=self._get_account_type(),
                balance=100
            )
            account.save()
