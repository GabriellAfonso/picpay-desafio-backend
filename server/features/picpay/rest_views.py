from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from features.picpay.serializers import TransactionSerializer, RecipientPreviewSerializer
from features.picpay.exceptions import TransactionExceptions
from features.picpay.repositories.account_repository import AccountRepository
from features.picpay.repositories.transaction_repository import TransactionRepository
from features.picpay.services.transaction_service import TransactionService
from features.picpay.validators.transaction_validator import TransactionValidator


class TransactionAPIView(APIView):

    def get(self, request):
        serializer = TransactionSerializer()
        return Response(serializer.data)

    @method_decorator(csrf_protect)
    def post(self, request):
        try:
            account_repo = AccountRepository()
            value = self._parse_value(request.data.get('value'))
            sender = account_repo.get_by_user_id(request.user.id)
            receiver = account_repo.get_by_document(request.data.get('document'))

            data = {'value': value, 'sender': sender, 'receiver': receiver}
            service = TransactionService(
                validator=TransactionValidator(),
                transaction_repo=TransactionRepository(),
            )
            result = service.process_transaction(data)
            serializer = TransactionSerializer(result)
            return Response(
                {'success': 'Transação autorizada e processada com sucesso', 'transaction': serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except TransactionExceptions as e:
            return Response({'error': e.message}, status=e.status_code)
        except Exception:
            return Response({'error': 'Erro interno ao processar a transação.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _parse_value(self, value: str) -> float:
        return float(value.replace('.', '').replace(',', '.'))


class RecipientPreviewAPIView(APIView):

    def get(self, request):
        document = request.query_params.get('document')
        if not document:
            return Response({'erro': 'Documento não informado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = AccountRepository().get_by_document(document)
        except TransactionExceptions:
            return Response({'erro': 'Destinatário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecipientPreviewSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)
