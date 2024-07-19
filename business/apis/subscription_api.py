import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime

from business.models.subscription_models import Plan, Subscriber
from business.models.models import Business
from business.permissions import IsBusinessOwner, IsBusinessMember, HasSubscriptionType, IsPlanValid
from utils.common import validate_required_fields, parse_duration



@api_view(['POST'])
@permission_classes([IsAuthenticated,IsBusinessOwner,HasSubscriptionType])
def add_plan(request):
    
    business_id = int(request.META.get("HTTP_X_BUSINESS_ID"))
    business = get_object_or_404(Business, id=business_id)
    
    data = json.loads(request.body)
    
    required_fields = ['name', 'duration', 'type', 'price']
    try:
        validate_required_fields(required_fields=required_fields,data=data)
    except ValidationError as e:
        return Response(e.detail, status=400)
    
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


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsBusinessOwner, HasSubscriptionType])
def delete_plan(request):
    business_id = int(request.META.get("HTTP_X_BUSINESS_ID"))
    plan_id = request.GET.get('id')
    
    try:
        plan = Plan.objects.get(id=plan_id, business_id=business_id)
    except Plan.DoesNotExist:
        return Response({"message": "Failed to delete the plan, invalid ID."}, status=status.HTTP_404_NOT_FOUND)
    
    plan.delete()
    
    return Response({"message": "Plan deleted successfully."}, status=status.HTTP_200_OK)     
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsBusinessMember, HasSubscriptionType, IsPlanValid])
def add_subscriber(request):
    user=request.user
    business_id = request.META.get("HTTP_X_BUSINESS_ID")
    
    data = json.loads(request.body)
    
    plan_id = data.get('plan') 
    
    if plan_id:
        required_fields=['name', 'email']
    else:
        required_fields=['name', 'email', 'start_date','end_date']
        
    
    try:
        validate_required_fields(required_fields=required_fields,data=data)
    except ValidationError as e:
        return Response(e.detail, status=400)
    
    name = data.get('name')
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if plan_id:
        plan = get_object_or_404(Plan, id=plan_id)
    else:
        plan=None
        
    business = get_object_or_404(Business, id=business_id)
    
    if start_date is None:
        start_date = timezone.now().date()
    else:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except:
            return Response({"message": "Invalid start_date format. Use YYYY-MM-DD."}, status=400)
            
    
    if end_date is None:
        try:
            duration_timedelta = parse_duration(plan.duration)
            end_date = start_date + duration_timedelta
        except ValueError as e:
            return Response({"message": str(e)}, status=400)
    else:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({"message": "Invalid end_date format. Use YYYY-MM-DD."}, status=400)

        
    subscriber = Subscriber.objects.create(
        name=name,
        business=business,
        plan=plan,
        email=email,
        phone=phone,
        plan_start_date=start_date,
        plan_end_date=end_date
    )
        
    subscriber_data = {
        "id": subscriber.id,
        "name": subscriber.name,
        "business": subscriber.business.id,
        "plan": subscriber.plan.id if plan else "-",
        "email": subscriber.email,
        "phone": subscriber.phone,
        "plan_start_date": subscriber.plan_start_date,
        "plan_end_date": subscriber.plan_end_date
    }
        
    return Response({"message": "Subscriber added successfully", "subscriber": subscriber_data})


@api_view(['GET'])
@permission_classes([IsAuthenticated,IsBusinessMember, HasSubscriptionType])
def get_subscriber(request):
    business_id = int(request.META.get("HTTP_X_BUSINESS_ID"))
    subscriber_id= request.GET.get('id')
    
    try:
        subscriber=Subscriber.objects.get(id=subscriber_id,business_id=business_id)
    except:
        return Response({"message":"Failed to fetch the subscriber, invalid ID."}, status=status.HTTP_404_NOT_FOUND)
    
    subscriber_data = {
            "id": subscriber.id,
            "name": subscriber.name,
            "email": subscriber.email,
            "plan": subscriber.plan.name,
            "duration": subscriber.plan.duration,
            "phone": subscriber.phone,
            "plan_start_date": subscriber.plan_start_date,
            "plan_end_date": subscriber.plan_end_date,
        }
    
    return Response({"message":"Subscriber fetched successfuly", "subscriber":subscriber_data},status=status.HTTP_200_OK)