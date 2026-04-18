from rest_framework.views import APIView
from .models import PicPayAccount
from apps.picpay.models import Transaction
from .serializers import TransactionSerializer, RecipientPreviewSerializer
from rest_framework.response import Response
from rest_framework import status
from .exceptions import TransactionExceptions
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from apps.picpay.services.transaction_service import TransactionService
from apps.picpay.validators.transaction_validator import TransactionValidator


class TransactionAPIView(APIView):
    """
    API REST para processar transações PicPay.
    """

    def get(self, request):
        serializer = TransactionSerializer()
        return Response(serializer.data)

    @method_decorator(csrf_protect)
    def post(self, request):
        try:
            value = self.process_value(request.data.get('value'))
            sender = self.get_sender(request.user.id)
            receiver = self.get_receiver(request.data.get('document'))

            data = {
                'value': value,
                'sender': sender,
                'receiver': receiver,
            }
            transaction_model = Transaction
            validator = TransactionValidator()
            transaction = TransactionService(
                validator=validator,
                transaction_model=transaction_model)
            transaction_process = transaction.process_transaction(data)
            serializer = TransactionSerializer(transaction_process)
            return Response(
                {'success': 'Transação autorizada e processada com sucesso',
                 'transaction': serializer.data},
                status=status.HTTP_201_CREATED
            )

        except TransactionExceptions as e:
            return Response({'error': e.message}, status=e.status_code)

        except PicPayAccount.DoesNotExist:
            return Response({'error': 'Conta não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': 'Erro interno ao processar a transação.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def process_value(self, value):
        v1 = value.replace('.', '')
        v2 = v1.replace(',', '.')
        return float(v2)

    def get_sender(self, id):
        sender = PicPayAccount.objects.get(user_id=id)
        return sender

    def get_receiver(self, doc):
        receiver = PicPayAccount.objects.get(document=doc)
        return receiver


class RecipientPreviewAPIView(APIView):

    def get(self, request):
        document = request.query_params.get('document')

        if not document:
            return Response({'erro': 'Documento não informado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = PicPayAccount.objects.get(document=document)
        except PicPayAccount.DoesNotExist:
            return Response({'erro': 'Destinatário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Retorna apenas os dados que devem ser exibidos para confirmação
        serializer = RecipientPreviewSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)
