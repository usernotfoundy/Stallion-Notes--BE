# Generated by Django 5.0.1 on 2024-04-23 17:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart_management', '0002_cart_seller'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='seller',
        ),
    ]
