from django.urls import path

from business.apis.api import CreateBusinessAndMapping, InviteToBusinessAPIView, AcceptDeclineInviteAPIView

urlpatterns = [
    path('create-business/', CreateBusinessAndMapping.as_view(), name='create-business'),
    path('invite/', InviteToBusinessAPIView.as_view(), name='invite-to-business'),
    path('invite-action/', AcceptDeclineInviteAPIView.as_view(), name='invite-action')
]
