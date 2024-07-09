from django.db import models
from django.conf import settings

class Business(models.Model):
    PRODUCT_BASED = 'product'
    SUBSCRIPTION_BASED = 'subscription'
    
    BUSINESS_TYPE_CHOICES = [
        (PRODUCT_BASED, 'Product Based'),
        (SUBSCRIPTION_BASED, 'Subscription Based'),
    ]

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=15,
        choices=BUSINESS_TYPE_CHOICES,
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
