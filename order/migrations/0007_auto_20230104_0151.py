# Generated by Django 3.1.1 on 2023-01-04 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_auto_20230104_0150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='childorderlineitems',
            name='product_image',
            field=models.TextField(blank=True, null=True),
        ),
    ]