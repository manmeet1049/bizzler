# Generated by Django 4.2.13 on 2024-07-19 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0018_subscriber_created_at_subscriber_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
