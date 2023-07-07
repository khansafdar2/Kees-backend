from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from products.Views import \
    Products, \
    Category, \
    Collection, \
    ProductGroup, \
    Variants, \
    Options, \
    Brand, \
    ProductImportExport

from products.DummyData import DummyData, SuperUserSignin
from products.BusinessLogic import MediaView
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication
from products.DataMigration.DataMigrationViews import VendorDataMigration, ProductGroupDataMigration, \
    CollectionDataMigration, BrandDataMigration, CategoryDataMigration, ProductDataMigration

urlpatterns = [
    # Products Crud
    path('product_list', Products.ProductListView.as_view(), name="ProductListView"),
    path('product', Products.ProductView.as_view(), name="ProductView"),
    path('product/<int:pk>', Products.ProductDetailView.as_view(), name="ProductDetailView"),
    path('products_status_change', Products.ProductStatusChange.as_view(), name="CollectionStatusChange"),
    path('products_bulk_organize', Products.ProductBulkOrganize.as_view(), name="ProductBulkOrganize"),
    path('products_bulk_tags', Products.ProductBulkTags.as_view(), name="ProductBulkTags"),
    path('products_export', ProductImportExport.ProductExport.as_view(), name="ProductExport"),
    path('products_import', ProductImportExport.ProductImport.as_view(), name="ProductImport"),
    path('category_position', Category.CategoryPosition.as_view(), name="CategoryPosition"),

    # Media Upload View
    path('media', MediaView.MediaView.as_view(), name="MediaView"),

    # Variants API (Create Update Delete)
    path('variant', Variants.VariantView.as_view(), name="VariantView"),
    path('variant/<int:pk>', Variants.VariantDetailView.as_view(), name="VariantDetailView"),
    path('variant_bulk_delete', Variants.BulkDeleteVariants.as_view(), name="BulkDeleteVariants"),

    # Get a variants inventory history
    path('inventory/<int:pk>', Variants.GetInventoryView.as_view(), name="GetInventoryView"),

    # Options API (Create Update Delete)
    path('options', Options.OptionView.as_view(), name="OptionView"),
    path('options/<int:pk>', Options.OptionDetailView.as_view(), name="OptionDetailView"),

    # Categories Multiple API based on requirements and generics
    path('categories', Category.CategoryView.as_view(), name="CategoryView"),
    path('main_category', Category.MainCategoryView.as_view(), name="MainCategoryView"),
    path('main_category/<int:pk>', Category.MainCategoryDetail.as_view(), name="MainCategoryDetail"),
    path('sub_category', Category.SubCategoryView.as_view(), name="SubCategoryView"),
    path('sub_category/<int:pk>', Category.SubCategoryDetail.as_view(), name="SubCategoryDetail"),
    path('super_sub_category', Category.SuperSubCategoryView.as_view(), name="SuperSubCategoryView"),
    path('super_sub_category/<int:pk>', Category.SuperSubCategoryDetail.as_view(), name="SuperSubCategoryDetail"),
    path('category_status_change', Category.CategoryAvailabilityChange.as_view(), name="CategoryAvailabilityChange"),

    # Collections API
    path('collections_list', Collection.CollectionListView.as_view(), name="CollectionListView"),
    path('collections', Collection.CollectionView.as_view(), name="CollectionView"),
    path('collections/<int:pk>', Collection.CollectionDetail.as_view(), name="CollectionView"),
    path('collections_status_change', Collection.CollectionStatusChange.as_view(), name="CollectionStatusChange"),

    # Product Groups API
    path('product_group_list', ProductGroup.ProductGroupListView.as_view(), name="ProductGroupListView"),
    path('product_group', ProductGroup.ProductGroupView.as_view(), name="ProductGroupView"),
    path('product_group/<int:pk>', ProductGroup.ProductGroupDetail.as_view(), name="ProductGroupDetail"),
    path('product_group_status_change', ProductGroup.ProductGroupStatusChange.as_view(), name="ProductGroupStatusChange"),

    # Product Brand
    path('brand_list', Brand.BrandListView.as_view(), name="BrandListView"),
    path('brand', Brand.BrandView.as_view(), name="BrandView"),
    path('brand/<int:pk>', Brand.BrandDetailView.as_view(), name="BrandDetail"),

    # Insert Dummy Data
    path('insert_dummy_data', DummyData.DummyDataInsert.as_view(), name="DummyDataInsert"),
    path('password_change', neglect_authentication(SuperUserSignin.PasswordChange), name="Get Token"),

    # Data Migration
    path('maincategorymigrate', CategoryDataMigration.MainCategoryMigrateView.as_view(), name="MainCategoryInsert"),
    path('subcategorymigrate', CategoryDataMigration.SubCategoryMigrateView.as_view(), name="SubCategoryInsert"),
    path('supersubcategorymigrate', CategoryDataMigration.SuperSubCategoryMigrateView.as_view(), name="SuperSubCategoryInsert"),
    path('vendor_migration', VendorDataMigration.VendorDataMigrateView.as_view(), name="VendorDataInsert"),
    path('collection_migration', CollectionDataMigration.CollectionMigrationView.as_view(), name="CollectionInsert"),
    path('productgroup_migration', ProductGroupDataMigration.ProductGroupMigrateView.as_view(), name="ProductGroupInsert"),
    path('productbrand_migration', BrandDataMigration.BrandMigrationView.as_view(), name="ProductBrandInsert"),
    path('product_migration', ProductDataMigration.ProductImport.as_view(), name="ProductInsert"),
    path('product_update', neglect_authentication(ProductDataMigration.ProductMigrationDataUpdate), name="ProductUpdate"),

]


schema_view = get_schema_view(
    openapi.Info(
        title="Product APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the Products application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('products/', include(urlpatterns))
    ],
)


urlpatterns += [
   # API Documentation route. (We are using Django Rest Swagger to sync with our API)
   path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]