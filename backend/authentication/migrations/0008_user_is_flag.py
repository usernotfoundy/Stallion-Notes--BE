# Generated by Django 5.0.1 on 2024-06-03 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_user_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_flag',
            field=models.BooleanField(default=False),
        ),
    ]
