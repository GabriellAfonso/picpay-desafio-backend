import os
from rest_framework import serializers
from .models import PicPayAccount, Transaction


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['value', 'sender', 'receiver']


class RecipientPreviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = PicPayAccount
        fields = ['complete_name']
