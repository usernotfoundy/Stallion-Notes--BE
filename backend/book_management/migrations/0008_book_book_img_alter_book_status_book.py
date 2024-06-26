# Generated by Django 5.0.1 on 2024-04-13 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_management', '0007_alter_book_status_book'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='book_img',
            field=models.ImageField(blank=True, null=True, upload_to='books'),
        ),
        migrations.AlterField(
            model_name='book',
            name='status_book',
            field=models.CharField(max_length=50),
        ),
    ]
