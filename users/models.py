from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from users.manager import CustomUserManager
from business.models import Business


class Auditable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
        
class User(AbstractBaseUser, PermissionsMixin, Auditable):
    
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

class UserBusinessMapping(Auditable,models.Model):
    USER_TYPE_CHOICES = (
        ('OWNER', 'OWNER'),
        ('STAFF', 'STAFF'),
    )
    
    user = models.ForeignKey(User, related_name='account_mappings', on_delete=models.CASCADE)
    business = models.ForeignKey(Business, related_name='user_mappings', on_delete=models.CASCADE,null=True)
    role = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.email} - {self.account.name}"
    
    class Meta:
        db_table = 'user_business_mapping'
    
    