from django.urls import path
from users.apis.unauthorized.apis import LoginAPIView, SignupAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('signup/', SignupAPIView.as_view(), name='signup'),
]
