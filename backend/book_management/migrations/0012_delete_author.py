# Generated by Django 5.0.1 on 2024-05-19 00:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book_management', '0011_alter_book_author'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Author',
        ),
    ]
