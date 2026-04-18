import pytest
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from features.picpay.models import PicPayAccount, Transaction
from features.picpay.services.profile_service import (
    fetch_recent_transactions,
    get_recent_profile_transactions,
)


def make_user(username, email):
    return User.objects.create_user(username=username, email=email, password="password123")


def make_account(user, document):
    return PicPayAccount.objects.create(
        user=user,
        complete_name="Gabriel Afonso",
        email=user.email,
        document=document,
        document_type="cpf",
        sex="M",
        account_type="personal",
        balance=Decimal("200.00"),
    )


def make_transaction(sender, receiver, value="50.00"):
    return Transaction.objects.create(
        sender=sender,
        receiver=receiver,
        value=Decimal(value),
    )


@pytest.mark.unit
class FetchRecentTransactionsTest(TestCase):

    def setUp(self):
        self.user_a = make_user("userA", "a@test.com")
        self.user_b = make_user("userB", "b@test.com")
        self.user_c = make_user("userC", "c@test.com")
        self.account_a = make_account(self.user_a, "111.111.111-11")
        self.account_b = make_account(self.user_b, "222.222.222-22")
        self.account_c = make_account(self.user_c, "333.333.333-33")

    def test_returns_transactions_where_account_is_sender(self):
        t = make_transaction(self.account_a, self.account_b)
        result = list(fetch_recent_transactions(self.account_a, limit=10))
        self.assertIn(t, result)

    def test_returns_transactions_where_account_is_receiver(self):
        t = make_transaction(self.account_b, self.account_a)
        result = list(fetch_recent_transactions(self.account_a, limit=10))
        self.assertIn(t, result)

    def test_does_not_return_transactions_from_other_accounts(self):
        t = make_transaction(self.account_b, self.account_c)
        result = list(fetch_recent_transactions(self.account_a, limit=10))
        self.assertNotIn(t, result)

    def test_respects_the_limit(self):
        make_transaction(self.account_a, self.account_b)
        make_transaction(self.account_a, self.account_b)
        make_transaction(self.account_a, self.account_b)
        result = list(fetch_recent_transactions(self.account_a, limit=2))
        self.assertEqual(len(result), 2)

    def test_returns_ordered_by_most_recent(self):
        t1 = make_transaction(self.account_a, self.account_b, "10.00")
        t2 = make_transaction(self.account_a, self.account_b, "20.00")
        result = list(fetch_recent_transactions(self.account_a, limit=10))
        self.assertEqual(result[0], t2)
        self.assertEqual(result[1], t1)


@pytest.mark.unit
class GetRecentProfileTransactionsTest(TestCase):

    def setUp(self):
        self.user_a = make_user("userA2", "a2@test.com")
        self.user_b = make_user("userB2", "b2@test.com")
        self.account_a = make_account(self.user_a, "444.444.444-44")
        self.account_b = make_account(self.user_b, "555.555.555-55")

    def test_returns_list_of_formatted_dicts(self):
        make_transaction(self.account_a, self.account_b)
        result = get_recent_profile_transactions(self.account_a, limit=3)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn('action', result[0])
        self.assertIn('time', result[0])
        self.assertIn('value', result[0])
        self.assertIn('counterpart', result[0])

    def test_action_is_sent_when_account_is_sender(self):
        make_transaction(self.account_a, self.account_b)
        result = get_recent_profile_transactions(self.account_a, limit=3)
        self.assertEqual(result[0]['action'], 'Enviou')

    def test_action_is_received_when_account_is_receiver(self):
        make_transaction(self.account_b, self.account_a)
        result = get_recent_profile_transactions(self.account_a, limit=3)
        self.assertEqual(result[0]['action'], 'Recebeu')

    def test_returns_empty_list_without_transactions(self):
        result = get_recent_profile_transactions(self.account_a, limit=3)
        self.assertEqual(result, [])

    def test_respects_transaction_limit(self):
        make_transaction(self.account_a, self.account_b)
        make_transaction(self.account_a, self.account_b)
        make_transaction(self.account_a, self.account_b)
        make_transaction(self.account_a, self.account_b)
        result = get_recent_profile_transactions(self.account_a, limit=2)
        self.assertEqual(len(result), 2)
