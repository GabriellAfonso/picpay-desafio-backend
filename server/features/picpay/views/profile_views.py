from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from features.picpay.repositories.account_repository import AccountRepository
from features.picpay.utils import get_first_and_last_name
from features.picpay.services.profile_service import get_recent_profile_transactions


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
