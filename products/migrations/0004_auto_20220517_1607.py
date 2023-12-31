# Generated by Django 3.1.1 on 2022-05-17 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_remove_product_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='seo_keywords',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='maincategory',
            name='seo_keywords',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='seo_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='seo_keywords',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='seo_title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='seo_keywords',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supersubcategory',
            name='seo_keywords',
            field=models.TextField(blank=True, null=True),
        ),
    ]
