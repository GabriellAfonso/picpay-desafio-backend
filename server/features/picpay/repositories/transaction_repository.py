from django.db.models import Q
from features.picpay.models import PicPayAccount, Transaction


class TransactionRepository:
    def create(self, sender: PicPayAccount, receiver: PicPayAccount, value) -> Transaction:
        transaction = Transaction(sender=sender, receiver=receiver, value=value)
        transaction.save()
        return transaction

    def get_recent_for_account(self, account: PicPayAccount, limit: int):
        return (
            Transaction.objects
            .filter(Q(sender=account) | Q(receiver=account))
            .select_related('sender', 'receiver')
            .order_by('-created_at')[:limit]
        )
