# Generated by Django 3.1.1 on 2023-02-28 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0004_discount_apply_on_discounted_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='apply_on_discounted_price',
            field=models.BooleanField(default=True),
        ),
    ]
