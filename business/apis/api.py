from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from business.models import Business, Invitation
from business.permissions import IsBusinessOwner
from users.models import UserBusinessMapping,User

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
        
        
        
class InviteToBusinessAPIView(APIView):
    permission_classes = [IsAuthenticated,IsBusinessOwner]

    def post(self, request):
        business_id = int(request.META["HTTP_X_BUSINESS_ID"])
        if not business_id:
            return Response({"error": "Business ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)

        inviter = request.user
        try:
            inviter_mapping = UserBusinessMapping.objects.get(user=inviter, business=business, role='OWNER')
        except UserBusinessMapping.DoesNotExist:
            return Response({"error": "You must be an owner of this business to send invites"}, status=status.HTTP_403_FORBIDDEN)

        invitee_email = request.data.get('email')
        invitee_role = request.data.get('role')

        if not invitee_email or not invitee_role:
            return Response({"error": "Email and role are required fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        existing_invitation = Invitation.objects.filter(email=invitee_email, business=business).first()
        if existing_invitation:
            if existing_invitation.status == Invitation.PENDING:
                return Response({"message": "An invitation has already been sent to this email."}, status=status.HTTP_200_OK)
            elif existing_invitation.status == Invitation.ACCEPTED:
                return Response({"message": "This user has already accepted an invitation to this business."}, status=status.HTTP_200_OK)

        invitee = User.objects.filter(email=invitee_email).first()

        if invitee:
            UserBusinessMapping.objects.create(user=invitee, business=business, role=invitee_role)
            return Response({"message": "User has been added to the business"}, status=status.HTTP_201_CREATED)
        else:
            Invitation.objects.create(email=invitee_email, business=business, role=invitee_role, invited_by=inviter)
            return Response({"message": "Invitation has been sent"}, status=status.HTTP_201_CREATED)



class AcceptDeclineInviteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        action = request.data.get('action').upper()
        invitation_id = request.data.get('invitation_id')

        if action not in ['ACCEPT', 'DECLINE']:
            return Response({"error": "Invalid action. Must be 'accept' or 'decline'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = Invitation.objects.get(id=invitation_id, email=user.email)
        except Invitation.DoesNotExist:
            return Response({"error": "Invitation not found."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'ACCEPT':
            if UserBusinessMapping.objects.filter(user=user, business=invitation.business).exists():
                return Response({"message": "User is already associated with this business."}, status=status.HTTP_200_OK)
            
            UserBusinessMapping.objects.create(
                user=user,
                business=invitation.business,
                role=invitation.role
            )
            invitation.status = Invitation.ACCEPTED
            invitation.save()

            return Response({"message": "Invitation accepted and user added to the business."}, status=status.HTTP_200_OK)

        elif action == 'DECLINE':
            invitation.status = Invitation.DECLINED
            invitation.save()
            return Response({"message": "Invitation declined."}, status=status.HTTP_200_OK)