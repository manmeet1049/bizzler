from rest_framework.permissions import BasePermission

from users.models import UserBusinessMapping, Business

class IsBusinessOwner(BasePermission):
    def has_permission(self, request, view):
        business_id = request.META.get("HTTP_X_BUSINESS_ID")
    
        if business_id is None:
            return False

        try:
            business_id = int(business_id)
        except ValueError:
            return False
        
        return UserBusinessMapping.objects.filter(user=request.user, business_id=business_id, role='OWNER').exists()
    
class IsBusinessMember(BasePermission):
    def has_permission(self, request, view):
        business_id = request.META.get("HTTP_X_BUSINESS_ID")
    
        if business_id is None:
            return False

        try:
            business_id = int(business_id)
        except ValueError:
            return False
        
        return UserBusinessMapping.objects.filter(user=request.user, business_id=business_id).exists()
    
class HasSubscriptionType(BasePermission):
    def has_permission(self, request, view):
        business_id = request.META.get("HTTP_X_BUSINESS_ID")
    
        if business_id is None:
            return False

        try:
            business_id = int(business_id)
        except ValueError:
            return False
        
        return Business.objects.filter(id=business_id,type=Business.SUBSCRIPTION_BASED).exists()
