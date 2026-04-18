import pytest
from apps.picpay.services.profile_service import humanize_date, format_transaction
from datetime import timedelta
from django.utils.timezone import now
from unittest.mock import patch, Mock


def fake_account(id):
    return Mock(id=id)


def fake_transaction():
    transaction = Mock()
    transaction.sender_id = 1
    transaction.receiver = Mock(complete_name="Receiver Name")
    transaction.sender = Mock(complete_name="Sender Name")
    transaction.created_at = now()
    transaction.value = 100
    return transaction


@pytest.mark.unit
def test_format_transaction_when_account_is_sender():
    transaction = fake_transaction()
    account = fake_account(1)
    format_result = format_transaction(transaction, account)
    assert format_result['action'] == 'Enviou'
    assert format_result['counterpart'] == 'Receiver Name'


@pytest.mark.unit
def test_format_transaction_when_account_is_receiver():
    transaction = fake_transaction()
    account = fake_account(2)
    format_result = format_transaction(transaction, account)
    assert format_result['action'] == 'Recebeu'
    assert format_result['counterpart'] == 'Sender Name'


@pytest.mark.unit
def test_humanize_date_today():
    assert humanize_date(now()) == "Hoje"


@pytest.mark.unit
def test_humanize_date_yesterday():
    assert humanize_date(now() - timedelta(days=1)) == "Ontem"


@pytest.mark.unit
def test_humanize_date_other_days():
    assert humanize_date(now() - timedelta(days=5)) == "5 dias atrás"
