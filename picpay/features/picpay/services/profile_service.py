from django.utils.timezone import now
from features.picpay.utils import get_first_and_last_name
from features.picpay.repositories.transaction_repository import TransactionRepository


def get_recent_profile_transactions(account, limit=3):
    transactions = fetch_recent_transactions(account, limit)
    return [format_transaction(t, account) for t in transactions]


def fetch_recent_transactions(account, limit):
    return TransactionRepository().get_recent_for_account(account, limit)


def format_transaction(transaction, account):
    is_sender = transaction.sender_id == account.id
    counterpart = transaction.receiver if is_sender else transaction.sender
    return {
        'action': 'Enviou' if is_sender else 'Recebeu',
        'time': humanize_date(transaction.created_at),
        'value': transaction.value,
        'counterpart': get_first_and_last_name(counterpart.complete_name),
    }


def humanize_date(date):
    days = (now() - date).days
    if days == 0:
        return 'Hoje'
    if days == 1:
        return 'Ontem'
    return f'{days} dias atrás'
