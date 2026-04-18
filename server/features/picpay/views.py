import random
import string
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rolepermissions.roles import assign_role
from features.picpay.forms import PicPayRegisterForm
from features.picpay.models import PicPayAccount
from features.picpay.repositories.account_repository import AccountRepository
from features.picpay.services.register_picpay_user import PicPayRegistrationService
from core.forms import EmailAuthenticationForm
from features.picpay.utils import get_first_and_last_name
from features.picpay.services.profile_service import get_recent_profile_transactions


class Login(View):

    def get(self, request):
        form = EmailAuthenticationForm(request=request)
        return render(request, 'picpay/login.html', {'form': form})

    def post(self, request):
        form = EmailAuthenticationForm(data=request.POST, request=request)
        if form.is_valid():
            auth.login(request, form.get_user())
            return redirect('picpay:profile')
        return render(request, 'picpay/login.html', {'form': form})


class Register(View):

    def get(self, request):
        return render(request, 'picpay/register.html', {
            'form': PicPayRegisterForm(),
            'created_account': False,
        })

    def post(self, request):
        form = PicPayRegisterForm(request.POST)
        if form.is_valid():
            PicPayRegistrationService(
                form=form.cleaned_data,
                account_repo=AccountRepository(),
            ).register()
            return redirect('picpay:login')
        return render(request, 'picpay/register.html', {'form': form})


class YourProfile(View):

    @method_decorator(login_required(login_url='picpay:login'))
    def get(self, request):
        account = AccountRepository().get_by_user_id(request.user.id)
        context = {
            'display_name': get_first_and_last_name(account.complete_name),
            'balance': account.balance,
            'sex': account.sex,
            'last_transactions': get_recent_profile_transactions(account, 2),
        }
        return render(request, 'picpay/profile.html', context)


class Logout(View):

    @method_decorator(login_required(login_url='picpay:login'))
    def get(self, request):
        logout(request)
        return redirect('picpay:login')


class GuestLogin(View):

    def get(self, request):
        username = 'guest_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        user = User.objects.create_user(username=username)
        user.set_unusable_password()
        user.save()
        assign_role(user, 'personal')
        PicPayAccount.objects.create(
            user=user,
            complete_name='Convidado',
            document=username,
            document_type='cpf',
            sex='M',
            account_type='personal',
            balance=100,
        )
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('picpay:profile')
