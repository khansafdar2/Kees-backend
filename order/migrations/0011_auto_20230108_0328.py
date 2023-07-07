# Generated by Django 3.1.1 on 2023-01-08 03:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20220524_1315'),
        ('order', '0010_auto_20230108_0307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='childorderlineitems',
            name='variant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='child_lineitem_variant', to='products.variant'),
        ),
        migrations.AlterField(
            model_name='lineitems',
            name='variant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='lineitem_variant', to='products.variant'),
        ),
    ]
