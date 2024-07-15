from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import LoginSerializer
from users.models import User
from business.models.models import Invitation

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user=get_object_or_404(User, id=user)
            login(request, user)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SignupAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(email=email, password=password)
        except IntegrityError:
            return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        pending_invitations = Invitation.objects.filter(email=email, status=Invitation.PENDING)
        pending_invitations_data = []
        for invitation in pending_invitations:
            pending_invitations_data.append({
                "id": invitation.id,
                "business": {
                    "id": invitation.business.id,
                    "name": invitation.business.name
                },
                "role": invitation.role,
                "status": invitation.status,
                "invited_by": {
                    "id": invitation.invited_by.id,
                    "email": invitation.invited_by.email
                }
            })

        return Response({
            "message": "User created successfully",
            "access": access_token,
            "refresh": refresh_token,
            "invitations": pending_invitations_data
        }, status=status.HTTP_201_CREATED)
