# Generated by Django 3.1.1 on 2022-05-24 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_auto_20220518_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='alt_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
