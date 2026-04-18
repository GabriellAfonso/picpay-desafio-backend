from apps.picpay.models import Transaction
from apps.picpay.utils import get_first_and_last_name
from django.db.models import Q
from django.utils.timezone import now


def get_recent_profile_transactions(account, limit=3):
    transactions = fetch_recent_transactions(account, limit)
    return [format_transaction(transaction, account) for transaction in transactions]


def fetch_recent_transactions(account, limit):
    return (
        Transaction.objects
        .filter(Q(sender=account) | Q(receiver=account))
        .select_related('sender', 'receiver')
        .order_by('-created_at')[:limit]
    )


def format_transaction(transaction, account):
    is_sender = transaction.sender_id == account.id
    action = "Enviou" if is_sender else "Recebeu"
    counterpart = transaction.receiver if is_sender else transaction.sender

    return {
        'action': action,
        'time': humanize_date(transaction.created_at),
        'value': transaction.value,
        'counterpart': get_first_and_last_name(counterpart.complete_name)
    }


def humanize_date(date):
    delta = now() - date
    days = delta.days
    if days == 0:
        return "Hoje"
    elif days == 1:
        return "Ontem"
    return f"{days} dias atrás"
