# Generated by Django 3.1.1 on 2022-05-24 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_feed', '0002_auto_20220517_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='custom_label5',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
