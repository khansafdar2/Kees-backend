# Generated by Django 3.1.1 on 2023-01-04 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_auto_20220920_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineitems',
            name='product_image',
            field=models.TextField(blank=True, null=True),
        ),
    ]