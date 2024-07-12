from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import UserBusinessMapping

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        print(email,password)
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid login credentials')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')

        refresh = RefreshToken.for_user(user)
        
        businesses = UserBusinessMapping.objects.filter(user=user)
        business_info = []
        for business in businesses:
            business_info.append({
                'business_id': business.business.id,
                'business_name': business.business.name,
                'role': business.role,
            })

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user':user.id,
            'email': user.email,
            'businesses': business_info
        }
