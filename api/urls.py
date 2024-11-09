from django.urls import path
from api.views import UserView, AiResponseView, TokenView, PasswordResetRequestAPI, PasswordResetConfirmAPI

urlpatterns = [
    path('users/', UserView.as_view(), name= 'users' ),
    path('tokens/', TokenView.as_view(), name= 'tokens'),
    path('ai-response/', AiResponseView.as_view(), name= 'ai-response'),
    path('password-reset/', PasswordResetRequestAPI.as_view(), name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmAPI.as_view(), name='password_reset_confirm'),
]