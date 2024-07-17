import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from business.models.subscription_models import Plan
from business.models.models import Business
from business.permissions import IsBusinessOwner, IsBusinessMember, HasSubscriptionType



@api_view(['POST'])
@permission_classes([IsAuthenticated,IsBusinessOwner,HasSubscriptionType])
def add_plan(request):
    
    business_id = int(request.META.get("HTTP_X_BUSINESS_ID"))
    business = get_object_or_404(Business, id=business_id)
    
    data = json.loads(request.body)
    
    required_fields = ['name', 'duration', 'type', 'price']
    missing_fields = [field for field in required_fields if not data.get(field)]  
    if missing_fields:
        return JsonResponse({"message": f"Missing fields: {', '.join(missing_fields)}"}, status=400)
    
    name = data.get('name')
    duration = data.get('duration')
    duration_type = data.get('type')
    price = data.get('price')

    if duration_type.upper() not in ['MONTHLY','YEARLY','DAILY','M','Y','D']:
        return Response({"message": "Invalid type, choices are: MONTHLY or M, YEARLY or Y, DAILY or D."}, status=status.HTTP_400_BAD_REQUEST)
    
    existing_plan = Plan.objects.filter(name=name, business=business).first()
    if existing_plan:
        existing_plan_data = {
            "id": existing_plan.id,
            "name": existing_plan.name,
            "duration": existing_plan.duration,
            "price": str(existing_plan.price),
            "added_by": existing_plan.added_by.id,
            "business": existing_plan.business.id
        }
        return Response({"message": "Plan already exists.", "plan": existing_plan_data}, status=status.HTTP_409_CONFLICT)
    
    plan = Plan.objects.create(
    name=name,
    price=price,
    added_by=request.user,
    business=business
    )
    
    plan.set_duration(duration, duration_type)
    plan.save()
    
    return Response({"message": "Plan added successfuly.", "id": plan.id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated,IsBusinessMember, HasSubscriptionType])
def get_plan(request):
    business_id = int(request.META.get("HTTP_X_BUSINESS_ID"))
    plan_id= request.GET.get('id')
    
    try:
        plan=Plan.objects.get(id=plan_id,business_id=business_id)
    except:
        return Response({"message":"Failed to fetch the plan, invalid ID."}, status=status.HTTP_404_NOT_FOUND)
    
    plan_data = {
            "id": plan.id,
            "name": plan.name,
            "duration": plan.duration,
            "price": str(plan.price),
            "added_by": plan.added_by.id,
            "business": plan.business.id
        }
    
    return Response({"message":"plan fetched successfuly", "plan":plan_data},status=status.HTTP_200_OK)
    
    
    
    



