# Generated by Django 5.1.2 on 2024-11-23 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0008_order_return_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]