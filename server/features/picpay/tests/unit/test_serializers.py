import pytest
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from features.picpay.models import PicPayAccount, Transaction
from features.picpay.serializers import TransactionSerializer, RecipientPreviewSerializer


def make_user(username, email):
    return User.objects.create_user(username=username, email=email, password="password123")


def make_account(user, document):
    return PicPayAccount.objects.create(
        user=user,
        complete_name="John Doe",
        email=user.email,
        document=document,
        document_type="cpf",
        sex="M",
        account_type="personal",
        balance=Decimal("200.00"),
    )


@pytest.mark.unit
class TransactionSerializerTest(TestCase):

    def setUp(self):
        sender_user = make_user("sender", "sender@test.com")
        receiver_user = make_user("receiver", "receiver@test.com")
        self.sender = make_account(sender_user, "111.111.111-11")
        self.receiver = make_account(receiver_user, "222.222.222-22")

    def test_valid_data_is_valid(self):
        data = {
            "value": "50.00",
            "sender": self.sender.pk,
            "receiver": self.receiver.pk,
        }
        serializer = TransactionSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serialized_fields_are_present(self):
        transaction = Transaction.objects.create(
            value=Decimal("50.00"),
            sender=self.sender,
            receiver=self.receiver,
        )
        serializer = TransactionSerializer(transaction)
        self.assertIn("value", serializer.data)
        self.assertIn("sender", serializer.data)
        self.assertIn("receiver", serializer.data)

    def test_serialized_value_is_correct(self):
        transaction = Transaction.objects.create(
            value=Decimal("75.00"),
            sender=self.sender,
            receiver=self.receiver,
        )
        serializer = TransactionSerializer(transaction)
        self.assertEqual(serializer.data["value"], "75.00")

    def test_value_is_read_only(self):
        serializer = TransactionSerializer()
        self.assertTrue(serializer.fields["value"].read_only)


@pytest.mark.unit
class RecipientPreviewSerializerTest(TestCase):

    def setUp(self):
        user = make_user("john", "john@test.com")
        self.account = make_account(user, "333.333.333-33")

    def test_serialized_fields_contains_complete_name(self):
        serializer = RecipientPreviewSerializer(self.account)
        self.assertIn("complete_name", serializer.data)

    def test_serialized_complete_name_is_correct(self):
        serializer = RecipientPreviewSerializer(self.account)
        self.assertEqual(serializer.data["complete_name"], "John Doe")

    def test_does_not_expose_sensitive_fields(self):
        serializer = RecipientPreviewSerializer(self.account)
        self.assertNotIn("document", serializer.data)
        self.assertNotIn("balance", serializer.data)
        self.assertNotIn("email", serializer.data)
