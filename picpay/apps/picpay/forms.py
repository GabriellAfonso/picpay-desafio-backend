from django import forms
from rolepermissions.roles import assign_role
from django import forms
from django.contrib.auth.models import User
from .models import PicPayAccount
import re
from validate_docbr import CPF, CNPJ
from django.db import transaction


class PicPayRegisterForm(forms.ModelForm):

    complete_name = forms.CharField(
        required=True,
        min_length=4,
        max_length=100,
        error_messages={
            'required': 'Este campo é obrigatório.',
            'min_length': 'Nome de usuário muito curto.',
            'max_length': 'Nome de usuário muito longo.',
        }
    )

    email = forms.EmailField(
        required=True,
        max_length=254,
        error_messages={
            'invalid': 'Utilize um e-mail válido',
        }
    )

    document = forms.CharField(
        required=True,
        max_length=50,
        error_messages={
            'required': 'Este campo é obrigatório.',
        }
    )

    sex = forms.ChoiceField(
        required=True,
        choices=[('M', 'Masculino'), ('F', 'Feminino')],
        error_messages={
            'required': 'Este campo é obrigatório.',
        }
    )

    password1 = forms.CharField(
        required=True,
        label='Password',
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        error_messages={
            'required': 'Este campo é obrigatório.',
        },
    )

    class Meta:
        model = User
        fields = ('complete_name', 'email', 'password1',
                  'document', 'sex',)

    def clean_complete_name(self):
        name = self.cleaned_data.get('complete_name')
        if not re.match("^[A-Za-zÀ-ÿ ]+$", name):
            raise forms.ValidationError('O nome deve conter apenas letras.')
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_email = self.instance.email

        if current_email != email:
            if User.objects.filter(email=email).exists():
                self.add_error(
                    'email',
                    forms.ValidationError(
                        'Este e-mail já esta sendo ultilizado.', code='invalid')
                )
        return email

    def clean_document(self):
        document = self.cleaned_data.get('document')
        digits_only = re.sub(r'\D', '', document)

        if len(digits_only) not in (11, 14):
            raise forms.ValidationError(
                'CPF/CNPJ inválido.')

        doc_type = self.cpf_or_cpnj(document)

        if doc_type == 'cpf':
            document = self.cpf_validator(digits_only)
            self.cleaned_data['document_type'] = 'cpf'
        if doc_type == 'cnpj':
            document = self.cnpj_validator(digits_only)
            self.cleaned_data['document_type'] = 'cnpj'
        return document

    def cpf_or_cpnj(self, document):
        digits_only = re.sub(r'\D', '', document)
        if len(digits_only) == 11:
            return 'cpf'
        return 'cnpj'

    def cpf_validator(self, document):
        cpf = CPF()
        doc = cpf.mask(document)
        if not cpf.validate(doc):
            raise forms.ValidationError('CPF inválido.')
        if PicPayAccount.objects.filter(document=doc).exists():
            raise forms.ValidationError('CPF já cadastrado.')

        return doc

    def cnpj_validator(self, document):
        cnpj = CNPJ()
        doc = cnpj.mask(document)
        if not cnpj.validate(doc):
            raise forms.ValidationError('CNPJ inválido.')
        if PicPayAccount.objects.filter(document=doc).exists():
            raise forms.ValidationError('CNPJ já cadastrado.')

        return doc

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < 6:
            raise forms.ValidationError(
                'A senha deve ter no mínimo 6 caracteres.'
            )
        return password1
