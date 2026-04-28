from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import auth
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from features.picpay.forms import PicPayRegisterForm
from features.picpay.repositories.account_repository import AccountRepository
from features.picpay.services.register_picpay_user import PicPayRegistrationService
from features.picpay.services.guest_login_service import GuestLoginService
from core.forms import EmailAuthenticationForm


class Login(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        form = EmailAuthenticationForm(request=request)
        return render(request, 'picpay/login.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = EmailAuthenticationForm(data=request.POST, request=request)
        if form.is_valid():
            auth.login(request, form.get_user())
            return redirect('picpay:profile')
        return render(request, 'picpay/login.html', {'form': form})


class Register(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'picpay/register.html', {
            'form': PicPayRegisterForm(),
            'created_account': False,
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        form = PicPayRegisterForm(request.POST)
        if form.is_valid():
            PicPayRegistrationService(
                form=form.cleaned_data,
                account_repo=AccountRepository(),
            ).register()
            return redirect('picpay:login')
        return render(request, 'picpay/register.html', {'form': form})


class Logout(View):

    @method_decorator(login_required(login_url='picpay:login'))
    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect('picpay:login')


class GuestLogin(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        user = GuestLoginService(AccountRepository()).create_guest()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('picpay:profile')
