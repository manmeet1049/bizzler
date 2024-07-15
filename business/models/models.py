from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Auditable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
class Business(Auditable,models.Model):
    PRODUCT_BASED = 'PRODUCT'
    SUBSCRIPTION_BASED = 'SUBSCRIPTION'
    
    BUSINESS_TYPE_CHOICES = [
        (PRODUCT_BASED, 'PRODUCT'),
        (SUBSCRIPTION_BASED, 'SUBSCRIPTION'),
    ]

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=18,
        choices=BUSINESS_TYPE_CHOICES,
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
 
class Invitation(Auditable,models.Model):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'
    
    STATUS_CHOICES = [
        (PENDING, 'PENDING'),
        (ACCEPTED, 'ACCEPTED'),
        (DECLINED, 'DECLINED'),
    ]
    USER_TYPE_CHOICES = (
        ('OWNER', 'OWNER'),
        ('STAFF', 'STAFF'),
    )

    email = models.EmailField()
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    role = models.CharField(max_length=20,choices=USER_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations_sent')

    def __str__(self):
        return f"Invitation to {self.email} for {self.business.name} as {self.role}"