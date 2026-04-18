from django.contrib.auth import authenticate
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class BaseRegisterForm(UserCreationForm):
    """
    Formulário base reutilizável para cadastro de usuários em múltiplos apps.
    """

    error_messages = {
        **UserCreationForm.error_messages,
        "password_mismatch": "As senhas não correspondem.",
    }

    username = forms.CharField(
        required=True,
        min_length=3,
        max_length=25,
        error_messages={
            'required': 'este campo é obrigatório.',
            'min_length': 'nome de usuário muito curto.',
            'max_length': 'nome de usuário muito grande.',
            'invalid': 'nome de usuário invalido, nao utilize espaços',
            'unique': 'Este nome de usuário já está em uso.',
        }
    )

    email = forms.EmailField(
        required=False,
        max_length=250,
        error_messages={
            'invalid': 'utilize um e-mail valido',
        }
    )

    password1 = forms.CharField(
        required=True,
        label='password',
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        error_messages={
            'required': 'este campo é obrigatório.',
        },
    )

    password2 = forms.CharField(
        required=True,
        label='password2',
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        error_messages={
            'required': 'este campo é obrigatório.',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_email = self.instance.email

        if current_email != email:

            if User.objects.filter(email=email).exists():
                self.add_error(
                    'email',
                    ValidationError(
                        'Este e-mail ja esta cadastrado', code='invalid')
                )
        return email


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label="E-mail")
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError("E-mail ou senha inválidos.")
        return self.cleaned_data

    def get_user(self):
        return self.user_cache
