from django.urls import path
from users.apis.unauthorized.apis import LoginAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
]
