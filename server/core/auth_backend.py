from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import HttpRequest


class EmailBackend(ModelBackend):
    """
    Backend de autenticação via email e senha.
    """

    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        *,
        email: str | None = None,
        **kwargs: object,
    ) -> User | None:
        if not email:
            # Não trata o caso username=..., deixa para o backend padrão
            return None
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
