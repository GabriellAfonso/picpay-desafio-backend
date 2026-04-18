import pytest
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from features.picpay.models import PicPayAccount, Transaction


def make_user(username="gabriel", email="gabriel@test.com"):
    return User.objects.create_user(username=username, email=email, password="password123")


def make_account(user, document="123.456.789-09", balance=Decimal("100.00")):
    account = PicPayAccount.objects.create(
        user=user,
        complete_name="Gabriel Afonso",
        email=user.email,
        document=document,
        document_type="cpf",
        sex="M",
        account_type="personal",
    )
    account.balance = balance
    account.save()
    return account


@pytest.mark.unit
class PicPayAccountPayTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.account = make_account(self.user, balance=Decimal("100.00"))

    def test_pay_deducts_value_from_balance(self):
        self.account.pay(Decimal("40.00"))
        self.assertEqual(self.account.balance, Decimal("60.00"))

    def test_pay_accepts_integer_value(self):
        self.account.pay(50)
        self.assertEqual(self.account.balance, Decimal("50.00"))

    def test_pay_accepts_string_value(self):
        self.account.pay("25.00")
        self.assertEqual(self.account.balance, Decimal("75.00"))


@pytest.mark.unit
class PicPayAccountReceiveTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.account = make_account(self.user, balance=Decimal("100.00"))

    def test_receive_adds_value_to_balance(self):
        self.account.receive(Decimal("50.00"))
        self.assertEqual(self.account.balance, Decimal("150.00"))

    def test_receive_accepts_integer_value(self):
        self.account.receive(50)
        self.assertEqual(self.account.balance, Decimal("150.00"))

    def test_receive_accepts_string_value(self):
        self.account.receive("25.00")
        self.assertEqual(self.account.balance, Decimal("125.00"))


@pytest.mark.unit
class PicPayAccountStrTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.account = make_account(self.user, document="123.456.789-09")

    def test_str_returns_name_and_document(self):
        self.assertEqual(str(self.account), "Gabriel Afonso (123.456.789-09)")


@pytest.mark.unit
class TransactionStrTest(TestCase):

    def setUp(self):
        sender_user = make_user(username="sender", email="sender@test.com")
        receiver_user = make_user(username="receiver", email="receiver@test.com")
        self.sender = make_account(sender_user, document="111.111.111-11")
        self.receiver = make_account(receiver_user, document="222.222.222-22")

    def test_str_with_sender_and_receiver(self):
        transaction = Transaction.objects.create(
            value=Decimal("50.00"),
            sender=self.sender,
            receiver=self.receiver,
        )
        self.assertEqual(
            str(transaction),
            "Gabriel Afonso send (50.00) to Gabriel Afonso"
        )

    def test_str_without_sender(self):
        transaction = Transaction.objects.create(
            value=Decimal("50.00"),
            sender=None,
            receiver=self.receiver,
        )
        self.assertEqual(
            str(transaction),
            "Usuário Removido send (50.00) to Gabriel Afonso"
        )

    def test_str_without_receiver(self):
        transaction = Transaction.objects.create(
            value=Decimal("50.00"),
            sender=self.sender,
            receiver=None,
        )
        self.assertEqual(
            str(transaction),
            "Gabriel Afonso send (50.00) to Usuário Removido"
        )
