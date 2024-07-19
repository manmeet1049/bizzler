from django.core.management.base import BaseCommand
from business.models.subscription_models import Subscription

class Command(BaseCommand):
    help = 'Update the status of all subscriptions based on the plan_end_date'

    def handle(self, *args, **kwargs):
        subscriptions = Subscription.objects.all()
        for subscription in subscriptions:
            subscription.check_and_update_status()
        self.stdout.write(self.style.SUCCESS('Successfully updated subscription statuses'))
