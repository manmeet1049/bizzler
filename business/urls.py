from django.urls import path

from business.apis.api import CreateBusinessAndMapping

urlpatterns = [
    path('create-business/', CreateBusinessAndMapping.as_view(), name='create-business')
]
