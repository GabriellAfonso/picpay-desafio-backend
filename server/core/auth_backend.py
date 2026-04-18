from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    """
    Backend de autenticação via email e senha.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email')
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
