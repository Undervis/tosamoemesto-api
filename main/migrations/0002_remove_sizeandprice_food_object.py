# Generated by Django 5.1.4 on 2025-01-31 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sizeandprice',
            name='food_object',
        ),
    ]
