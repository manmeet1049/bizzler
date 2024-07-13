from rest_framework.permissions import BasePermission

from users.models import UserBusinessMapping

class IsBusinessOwner(BasePermission):
    def has_permission(self, request, view):
        business_id = int(request.META["HTTP_X_BUSINESS_ID"])
        
        if not business_id:
            return False
        
        return UserBusinessMapping.objects.filter(user=request.user, business_id=business_id, role='OWNER').exists()
