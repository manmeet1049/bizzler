from django.urls import path

from business.apis.api import CreateBusinessAndMapping, InviteToBusinessAPIView, AcceptDeclineInviteAPIView
from business.apis.subscription_api import add_plan,get_plan

urlpatterns = [
    path('create-business/', CreateBusinessAndMapping.as_view(), name='create-business'),
    path('invite/', InviteToBusinessAPIView.as_view(), name='invite-to-business'),
    path('invite-action/', AcceptDeclineInviteAPIView.as_view(), name='invite-action'),
    
    # subscriber based business apis
    path('subscribers/add-plan/', add_plan, name='add-plan'),
    path('subscribers/get-plan/', get_plan, name='get-plan')
    
]
