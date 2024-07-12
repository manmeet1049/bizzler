from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated

from business.models import Business
from users.models import UserBusinessMapping

class CreateBusinessAndMapping(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        data = request.data
        
        business_name = data.get('name')
        business_type = data.get('type')
        business_phone = data.get('phone')
        business_address = data.get('address')

        if not business_name or not business_type:
            return Response({"error": "Name and type are required fields for business"}, status=status.HTTP_400_BAD_REQUEST)
        
        if Business.objects.filter(name=business_name, owner=user).exists():
            return Response({"error": "Business with this name already exists for this owner"}, status=status.HTTP_400_BAD_REQUEST)

        business = Business.objects.create(
            name=business_name,
            owner=user,
            type=business_type,
            phone=business_phone,
            address=business_address
        )

        user_business_map=UserBusinessMapping.objects.create(
            user=user,
            business=business,
            role='OWNER'
        )

        return Response({
            "business_id": business.id,
            "business_name": business.name,
            "user_id": user.id,
            "role": user_business_map.role
        }, status=status.HTTP_201_CREATED)
