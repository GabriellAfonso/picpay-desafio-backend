import random
import string
from django.contrib.auth.models import User
from rolepermissions.roles import assign_role
from features.picpay.repositories.account_repository import AccountRepository


class GuestLoginService:

    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo

    def create_guest(self) -> User:
        username = 'guest_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        user = self.account_repo.create_guest_user(username)
        assign_role(user, 'personal')
        self.account_repo.create_account(user, {
            'complete_name': 'Convidado',
            'document': username,
            'document_type': 'cpf',
            'sex': 'M',
            'account_type': 'personal',
        })
        return user
