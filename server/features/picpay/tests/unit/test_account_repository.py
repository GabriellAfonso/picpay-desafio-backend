import pytest
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from features.picpay.models import PicPayAccount
from features.picpay.repositories.account_repository import AccountRepository
from features.picpay.exceptions import AccountDoesNotExist


def make_user(username="john", email="john@test.com"):
    return User.objects.create_user(username=username, email=email, password="pass123")


def make_account(user, document="123.456.789-09"):
    return PicPayAccount.objects.create(
        user=user,
        complete_name="John Doe",
        email=user.email,
        document=document,
        document_type="cpf",
        sex="M",
        account_type="personal",
        balance=Decimal("100.00"),
    )


@pytest.mark.unit
class AccountRepositoryGetByUserIdTest(TestCase):

    def setUp(self):
        self.repo = AccountRepository()
        self.user = make_user()
        self.account = make_account(self.user)

    def test_returns_account_for_existing_user(self):
        result = self.repo.get_by_user_id(self.user.id)
        self.assertEqual(result, self.account)

    def test_raises_account_does_not_exist_for_unknown_id(self):
        with self.assertRaises(AccountDoesNotExist):
            self.repo.get_by_user_id(99999)


@pytest.mark.unit
class AccountRepositoryGetByDocumentTest(TestCase):

    def setUp(self):
        self.repo = AccountRepository()
        self.user = make_user()
        self.account = make_account(self.user, document="123.456.789-09")

    def test_returns_account_for_existing_document(self):
        result = self.repo.get_by_document("123.456.789-09")
        self.assertEqual(result, self.account)

    def test_raises_account_does_not_exist_for_unknown_document(self):
        with self.assertRaises(AccountDoesNotExist):
            self.repo.get_by_document("000.000.000-00")


@pytest.mark.unit
class AccountRepositoryCreateGuestUserTest(TestCase):

    def setUp(self):
        self.repo = AccountRepository()

    def test_creates_user_with_given_username(self):
        user = self.repo.create_guest_user("guest_abc123")
        self.assertEqual(user.username, "guest_abc123")

    def test_returns_user_instance(self):
        user = self.repo.create_guest_user("guest_xyz")
        self.assertIsInstance(user, User)

    def test_user_is_persisted_in_db(self):
        self.repo.create_guest_user("guest_persisted")
        self.assertTrue(User.objects.filter(username="guest_persisted").exists())
