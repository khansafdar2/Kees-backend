# Generated by Django 3.1.1 on 2022-09-20 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_auto_20220920_1707'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='childorderlineitems',
            name='discounted_price',
        ),
        migrations.RemoveField(
            model_name='lineitems',
            name='discounted_price',
        ),
        migrations.AddField(
            model_name='checkout',
            name='discounted_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='childorder',
            name='discounted_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='discounted_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
