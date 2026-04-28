from datetime import datetime
from django.utils.timezone import now
from features.picpay.models import PicPayAccount, Transaction
from features.picpay.utils import get_first_and_last_name
from features.picpay.repositories.transaction_repository import TransactionRepository


class ProfileService:

    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def get_recent_transactions(self, account: PicPayAccount, limit: int = 3) -> list[dict]:
        transactions = self.transaction_repo.get_recent_for_account(account, limit)
        return [format_transaction(t, account) for t in transactions]


def format_transaction(transaction: Transaction, account: PicPayAccount) -> dict:
    is_sender = transaction.sender_id == account.id
    counterpart = transaction.receiver if is_sender else transaction.sender
    counterpart_name = counterpart.complete_name if counterpart else 'Usuário Removido'
    return {
        'action': 'Enviou' if is_sender else 'Recebeu',
        'time': humanize_date(transaction.created_at),
        'value': transaction.value,
        'counterpart': get_first_and_last_name(counterpart_name),
    }


def humanize_date(date: datetime) -> str:
    days = (now() - date).days
    if days == 0:
        return 'Hoje'
    if days == 1:
        return 'Ontem'
    return f'{days} dias atrás'
