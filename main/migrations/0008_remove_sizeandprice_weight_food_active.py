# Generated by Django 5.1.4 on 2025-02-21 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_remove_food_weight_sizeandprice_weight'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sizeandprice',
            name='weight',
        ),
        migrations.AddField(
            model_name='food',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
