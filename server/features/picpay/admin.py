from django.contrib import admin
from .models import PicPayAccount, Transaction

admin.site.register(PicPayAccount)


class TransactionAdmin(admin.ModelAdmin):
    readonly_fields = ('value', 'sender', 'receiver', 'created_at')
    list_display = ('value', 'sender', 'receiver', 'created_at')

    def has_delete_permission(self, request, obj=None):
        # Não permite a exclusão de objetos
        return False

    def has_add_permission(self, request):
        # Não permite a adição de novos objetos
        return False


admin.site.register(Transaction, TransactionAdmin)
