# Generated by Django 5.0.1 on 2024-05-12 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_management', '0008_book_book_img_alter_book_status_book'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='wishlist',
            field=models.BigIntegerField(default=0),
        ),
    ]