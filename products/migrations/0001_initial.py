# Generated by Django 3.1.1 on 2022-04-24 02:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('handle', models.CharField(blank=True, max_length=200, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='BrandHandle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='CategoryHandle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('count', models.IntegerField(default=0)),
                ('category_type', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('handle', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('collection_type', models.CharField(blank=True, max_length=200, null=True)),
                ('slug', models.CharField(blank=True, max_length=200, null=True)),
                ('seo_title', models.CharField(blank=True, max_length=200, null=True)),
                ('seo_description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=250, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='CollectionHandle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='CollectionMetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('field', models.CharField(blank=True, max_length=200, null=True)),
                ('value', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollectionRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('column', models.CharField(blank=True, max_length=200, null=True)),
                ('relation', models.CharField(blank=True, max_length=200, null=True)),
                ('condition', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('feature_title', models.CharField(blank=True, max_length=200, null=True)),
                ('feature_details', models.TextField(blank=True, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='InventoryHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('event', models.TextField(blank=True, null=True)),
                ('adjusted_by', models.TextField(blank=True, null=True)),
                ('adjustment', models.IntegerField(blank=True, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='MainCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('handle', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('availability', models.BooleanField(default=True)),
                ('position', models.IntegerField(default=0)),
                ('slug', models.CharField(blank=True, max_length=200, null=True)),
                ('seo_title', models.CharField(blank=True, max_length=200, null=True)),
                ('seo_description', models.TextField(blank=True, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='MainCategoryMetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('field', models.CharField(blank=True, max_length=200, null=True)),
                ('value', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('file_name', models.TextField(blank=True, null=True)),
                ('file_path', models.TextField(blank=True, null=True)),
                ('cdn_link', models.TextField(blank=True, null=True)),
                ('position', models.IntegerField(default=0)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('position', models.IntegerField(blank=True, null=True)),
                ('values', models.TextField(blank=True, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('product_type', models.CharField(blank=True, max_length=200, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('warranty', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.CharField(blank=True, max_length=250, null=True)),
                ('has_variants', models.BooleanField(default=False)),
                ('whatsapp', models.BooleanField(default=True)),
                ('track_inventory', models.BooleanField(default=False)),
                ('cod_available', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('hide_out_of_stock', models.BooleanField(default=False)),
                ('is_hidden', models.BooleanField(default=False)),
                ('handle', models.CharField(blank=True, max_length=200, null=True)),
                ('tags', models.TextField(blank=True, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ProductGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('handle', models.CharField(blank=True, max_length=250, null=True)),
                ('tat', models.CharField(blank=True, max_length=250, null=True)),
                ('status', models.CharField(blank=True, max_length=250, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ProductGroupHandle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ProductHandle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('handle', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('availability', models.BooleanField(default=True)),
                ('position', models.IntegerField(default=0)),
                ('slug', models.CharField(blank=True, max_length=200, null=True)),
                ('seo_title', models.CharField(blank=True, max_length=200, null=True)),
                ('seo_description', models.TextField(blank=True, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('main_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_main_category', to='products.maincategory')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='SuperSubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('handle', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('availability', models.BooleanField(default=True)),
                ('position', models.IntegerField(default=0)),
                ('slug', models.CharField(blank=True, max_length=200, null=True)),
                ('seo_title', models.CharField(blank=True, max_length=200, null=True)),
                ('seo_description', models.TextField(blank=True, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('sub_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='super_sub_category', to='products.subcategory')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_option', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('sku', models.CharField(max_length=200, null=True, unique=True)),
                ('position', models.IntegerField(blank=True, null=True)),
                ('compare_at_price', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('cost_per_item', models.CharField(blank=True, max_length=200, null=True)),
                ('option1', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('option2', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('option3', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('taxable', models.BooleanField(default=True)),
                ('barcode', models.CharField(blank=True, max_length=200, null=True)),
                ('is_physical', models.BooleanField(default=True)),
                ('weight', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('weight_unit', models.CharField(blank=True, max_length=200, null=True)),
                ('inventory_quantity', models.IntegerField(blank=True, null=True)),
                ('old_inventory_quantity', models.IntegerField(blank=True, null=True)),
                ('legacy_product', models.IntegerField(blank=True, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_variant', to='products.product')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='SuperSubCategoryMetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('field', models.CharField(blank=True, max_length=150, null=True)),
                ('value', models.TextField(blank=True, null=True)),
                ('super_sub_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='super_sub_category_meta_data', to='products.supersubcategory')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubCategoryMetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('field', models.CharField(blank=True, max_length=200, null=True)),
                ('value', models.TextField(blank=True, null=True)),
                ('sub_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_category_meta_data', to='products.subcategory')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubCategoryCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('column', models.CharField(blank=True, max_length=200, null=True)),
                ('relation', models.CharField(blank=True, max_length=200, null=True)),
                ('condition', models.CharField(blank=True, max_length=200, null=True)),
                ('sub_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_category_condition', to='products.subcategory')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddIndex(
            model_name='producthandle',
            index=models.Index(fields=['id', 'name'], name='products_pr_id_09f0d3_idx'),
        ),
        migrations.AddIndex(
            model_name='productgrouphandle',
            index=models.Index(fields=['id', 'name'], name='products_pr_id_308dee_idx'),
        ),
    ]
