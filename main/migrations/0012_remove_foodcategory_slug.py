# Generated by Django 5.1.4 on 2025-02-27 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_sizeandprice_weight'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodcategory',
            name='slug',
        ),
    ]
