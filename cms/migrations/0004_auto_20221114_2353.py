# Generated by Django 3.1.1 on 2022-11-14 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20221114_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]