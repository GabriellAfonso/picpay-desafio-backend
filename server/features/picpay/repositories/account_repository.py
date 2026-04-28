from typing import Any
from django.contrib.auth.models import User
from features.picpay.models import PicPayAccount
from features.picpay.exceptions import AccountDoesNotExist


class AccountRepository:
    def create_user(self, email: str, password: str) -> User:
        user = User(email=email, username=email)
        user.set_password(password)
        user.save()
        return user

    def create_account(self, user: User, form_data: dict) -> PicPayAccount:
        account = PicPayAccount(
            user=user,
            complete_name=form_data['complete_name'],
            document=form_data['document'],
            document_type=form_data['document_type'],
            sex=form_data['sex'],
            account_type=form_data['account_type'],
            balance=100,
        )
        account.save()
        return account

    def create_guest_user(self, username: str) -> User:
        return User.objects.create_user(username=username)

    def get_by_user_id(self, user_id: Any) -> PicPayAccount:
        try:
            return PicPayAccount.objects.get(user_id=user_id)
        except PicPayAccount.DoesNotExist:
            raise AccountDoesNotExist()

    def get_by_document(self, document: Any) -> PicPayAccount:
        try:
            return PicPayAccount.objects.get(document=document)
        except PicPayAccount.DoesNotExist:
            raise AccountDoesNotExist()
