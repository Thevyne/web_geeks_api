from django.urls import path
from api.views import UserView, AiResponseView, TokenView

urlpatterns = [
    path('users/', UserView.as_view(), name= 'users' ),
    path('tokens/', TokenView.as_view(), name= 'tokens'),
    path('ai-response/', AiResponseView.as_view(), name= 'ai-response'),
]