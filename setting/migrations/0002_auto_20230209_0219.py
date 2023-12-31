# Generated by Django 3.1.1 on 2023-02-09 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoyaltySetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('amount_equal_point', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('point_equal_amount', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('start_loyalty_amount', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('minimum_orders_loyalty_start', models.IntegerField(default=0)),
                ('minimum_point_redeem', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('platform', models.TextField(blank=True, null=True)),
                ('order_url', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('spending_amount', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('no_of_point', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('no_of_order', models.PositiveIntegerField(blank=True, null=True)),
                ('type', models.CharField(blank=True, max_length=200, null=True)),
                ('paid_order', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False)),
                ('start_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('end_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddIndex(
            model_name='rule',
            index=models.Index(fields=['deleted'], name='setting_rul_deleted_ea6bd5_idx'),
        ),
        migrations.AddIndex(
            model_name='loyaltysetting',
            index=models.Index(fields=['deleted'], name='setting_loy_deleted_06accd_idx'),
        ),
    ]
