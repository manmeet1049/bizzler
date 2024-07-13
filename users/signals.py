
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth import get_user_model

# from business.models import Invitation
# from users.models import  UserBusinessMapping

# User = get_user_model()

# @receiver(post_save, sender=User)
# def check_invitations_and_assign_business(instance, created, **kwargs):
#     if created:  
#         invitations = Invitation.objects.filter(email=instance.email, status=Invitation.PENDING)
#         for invitation in invitations:
#             business = invitation.business
#             role = invitation.role
#             UserBusinessMapping.objects.create(user=instance, business=business, role=role)
#             invitation.status = Invitation.ACCEPTED
#             invitation.save()
