# Generated by Django 5.0.1 on 2024-04-13 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_management', '0006_remove_book_upload_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='status_book',
            field=models.CharField(default='pending', max_length=50),
        ),
    ]