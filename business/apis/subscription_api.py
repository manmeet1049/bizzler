import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime

from business.models.subscription_models import Plan, Subscriber, Transaction, Subscription
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
        required_fields=['name', 'email', 'start_date','end_date','amount']
        
    
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
    amount=data.get('amount')
    
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
        email=email,
        phone=phone,
    )
    
    subscription= Subscription.objects.create(
        subscriber=subscriber,
        plan=plan,
        plan_start_date=start_date,
        plan_end_date=end_date
        
    )
    transaction= Transaction.objects.create(
        plan=subscription.plan,
        conducted_by=user,
        business=business,
        amount= amount if amount else subscription.plan.price
    )
    
    subscription.transaction=transaction
    subscription.save()
        
    subscriber_data = {
        "id": subscriber.id,
        "name": subscriber.name,
        "business": subscriber.business.id,
        "email": subscriber.email,
        "phone": subscriber.phone,
    }
    subscription_data={
        "id":subscription.id,
        "plan": subscription.plan.id if plan else "-",
        "plan_start_date": subscription.plan_start_date,
        "plan_end_date": subscription.plan_end_date,
        'transaction':transaction.id
    }
        
    return Response({"message": "Subscriber added successfully", "subscriber_details": subscriber_data,"subscription_details":subscription_data},status=status.HTTP_201_CREATED)


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
            "phone": subscriber.phone,
        }
    try:
        active_subscription= Subscription.objects.get(subscriber=subscriber,active=True)
        active_subscription_data={
            "id":active_subscription.id,
            "plan":active_subscription.plan.name if active_subscription.plan else "-",
            "duration":active_subscription.plan.duration if active_subscription.plan else "-",
            "start_date":active_subscription.plan_start_date,
            "end_date":active_subscription.plan_end_date,
        }
    except:
        active_subscription_data= None
    
    return Response({"message":"Subscriber fetched successfuly", "subscriber":subscriber_data,"active_subscription":active_subscription_data},status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsBusinessMember, HasSubscriptionType, IsPlanValid])
def renew_subscription(request):
    user=request.user
    business_id = request.META.get("HTTP_X_BUSINESS_ID")
    
    data = json.loads(request.body)
    
    plan_id = data.get('plan') 
    
    if plan_id:
        required_fields=['subscriber']
    else:
        required_fields=['subscriber','start_date','end_date','amount']
        
    
    try:
        validate_required_fields(required_fields=required_fields,data=data)
    except ValidationError as e:
        return Response(e.detail, status=400)
    
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    amount=data.get('amount')
    subscriber=data.get('subscriber')
    
    try:
        existing_active_subscription = Subscription.objects.filter(
        subscriber=subscriber,
        active=True
                    ).order_by('-created_at').first()
        existing_active_subscription.check_and_update_status()
        print('existing: ',existing_active_subscription)
        
    except:
        existing_active_subscription=None
        
    
    if plan_id:
        plan = get_object_or_404(Plan, id=plan_id)
    else:
        plan=None
        
    business = get_object_or_404(Business, id=business_id)
    
    if start_date is None:
        if existing_active_subscription:
            start_date = existing_active_subscription.plan_end_date
        else:
            start_date=timezone.now().date()
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

        
    subscriber = get_object_or_404(Subscriber, id=subscriber)
    
    subscription= Subscription.objects.create(
        subscriber=subscriber,
        plan=plan,
        plan_start_date=start_date,
        plan_end_date=end_date
        
    )
    transaction= Transaction.objects.create(
        plan=subscription.plan,
        conducted_by=user,
        business=business,
        amount= amount if amount else subscription.plan.price
    )
    
    subscription.transaction=transaction
    subscription.save()
        
    subscriber_data = {
        "id": subscriber.id,
        "name": subscriber.name,
        "business": subscriber.business.id,
        "email": subscriber.email,
        "phone": subscriber.phone,
    }
    subscription_data={
        "id":subscription.id,
        "plan": subscription.plan.id if plan else "-",
        "plan_start_date": subscription.plan_start_date,
        "plan_end_date": subscription.plan_end_date,
        'transaction':transaction.id
    }
        
    return Response(
                    {"message": "Subscription renewed successfully",
                     "qued": True if existing_active_subscription else False,
                     "subscriber_details": subscriber_data,
                     "previos_subscription":"Previous Subscription found." if existing_active_subscription else "Didn't have previously active subscription",
                     "new_subscription_details":subscription_data},
                      status=status.HTTP_201_CREATED
                      )