from django.db import models
from django.conf import settings

from business.models.models import Auditable, Business
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Plan(Auditable,models.Model):
    
    name=models.CharField(max_length=50,null=True)
    duration = models.CharField(max_length=10, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_by=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business = models.ForeignKey(Business,on_delete=models.CASCADE)
    
    
    class Meta:
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"
        db_table='subscription_plans'
        
    def set_duration(self, count, d_type):
        duration_dict= {"MONTHLY":"M",
                 "YEARLY":"Y",
                 "DAILY":"D"
                 }
        
        d_type= d_type if not duration_dict.get(d_type) else duration_dict[d_type]
        
        self.duration = f"{count} {d_type}"
        
        
class Subscriber(Auditable,models.Model):
    name = models.CharField(max_length=255)
    business = models.ForeignKey(Business,on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True)

    class Meta:
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"
        db_table='subscription_subscribers'
        

    def __str__(self):
        return self.name
        
        
class Transaction(Auditable,models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    conducted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business,on_delete=models.CASCADE)  

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        db_table='subscription_transactions'

    def __str__(self):
        return f"Transaction by {self.customer.name} for {self.product.name}"
    
class Subscription(Auditable,models.Model):
    subscriber=models.ForeignKey(Subscriber,on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan,on_delete=models.CASCADE,null=True)
    plan_start_date = models.DateField()
    plan_end_date = models.DateField()
    transaction= models.ForeignKey('Transaction', null=True, on_delete=models.CASCADE)
    active=models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        db_table='subscription_subscriptions'
        

    def __str__(self):
        return self.subscriber.name
    
    def check_and_update_status(self):
        print(self)
        if self.plan_end_date < timezone.now().date():
            self.active = False
            self.save()