from django.contrib import admin
from django.db.models import Model
from django.http import HttpRequest
from .models import PicPayAccount, Transaction

admin.site.register(PicPayAccount)


class TransactionAdmin(admin.ModelAdmin):
    readonly_fields = ('value', 'sender', 'receiver', 'created_at')
    list_display = ('value', 'sender', 'receiver', 'created_at')

    def has_delete_permission(self, request: HttpRequest, obj: Model | None = None) -> bool:
        # Não permite a exclusão de objetos
        return False

    def has_add_permission(self, request: HttpRequest) -> bool:
        # Não permite a adição de novos objetos
        return False


admin.site.register(Transaction, TransactionAdmin)
