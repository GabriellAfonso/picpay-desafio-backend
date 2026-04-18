from django.urls import path
from features.picpay.views.auth_views import Login, Register, Logout, GuestLogin
from features.picpay.views.profile_views import YourProfile
from features.picpay.views.api_views import TransactionAPIView, RecipientPreviewAPIView

app_name = 'picpay'

urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('cadastro/', Register.as_view(), name='register'),
    path('Seu-perfil/', YourProfile.as_view(), name='profile'),
    path('logout/', Logout.as_view(), name='logout'),
    path('guest/', GuestLogin.as_view(), name='guest_login'),
    path('api/transaction/', TransactionAPIView.as_view(), name='api_transaction'),
    path('api/recipient-preview/', RecipientPreviewAPIView.as_view(), name='recipient_preview'),
]
