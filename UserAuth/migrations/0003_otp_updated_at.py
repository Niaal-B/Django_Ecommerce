# Generated by Django 5.1.2 on 2024-10-23 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserAuth', '0002_alter_otp_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='otp',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
