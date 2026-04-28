from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
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
    serializer_class = TransactionSerializer

    def get(self, request: Request) -> Response:
        return Response(TransactionSerializer().data)

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        try:
            raw_value = request.data.get('value')
            raw_document = request.data.get('document')
            if not isinstance(raw_value, str) or not isinstance(raw_document, str):
                return Response(
                    {'error': 'Campos value e document são obrigatórios.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            assert request.user.pk is not None
            account_repo = AccountRepository()
            value = self._parse_value(raw_value)
            sender = account_repo.get_by_user_id(request.user.pk)
            receiver = account_repo.get_by_document(raw_document)

            result = TransactionService(
                validator=TransactionValidator(),
                transaction_repo=TransactionRepository(),
            ).process_transaction({'value': value, 'sender': sender, 'receiver': receiver})

            return Response(
                {'success': 'Transação autorizada e processada com sucesso',
                 'transaction': TransactionSerializer(result).data},
                status=status.HTTP_201_CREATED,
            )
        except TransactionExceptions as e:
            return Response({'error': e.message}, status=e.status_code)
        except Exception:
            return Response(
                {'error': 'Erro interno ao processar a transação.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _parse_value(self, value: str) -> float:
        return float(value.replace('.', '').replace(',', '.'))


class RecipientPreviewAPIView(APIView):
    serializer_class = RecipientPreviewSerializer

    def get(self, request: Request) -> Response:
        document = request.query_params.get('document')
        if not document:
            return Response({'erro': 'Documento não informado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = AccountRepository().get_by_document(document)
        except TransactionExceptions:
            return Response({'erro': 'Destinatário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(RecipientPreviewSerializer(account).data, status=status.HTTP_200_OK)
