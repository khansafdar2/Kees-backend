
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from cms.Views import Pages, Preferences, Menu, PriceRange, StoreFilter, Customization, Navigation, Blog, BlogCategory


urlpatterns = [
   # All CMS CRUD APIs needed
   path('pages', Pages.PagesView.as_view(), name="PagesView"),
   path('pages/<int:pk>', Pages.PagesDetailView.as_view(), name="PagesDetailView"),
   path('preferences', Preferences.PreferencesView.as_view(), name="PreferencesView"),
   path('menu', Menu.MenuView.as_view(), name="MenuView"),

   path('homepage', Customization.HomePageView.as_view(), name="HomePage"),
   path('header', Customization.HeaderView.as_view(), name="Header"),
   path('footer', Customization.FooterView.as_view(), name="Footer"),
   path('customization', Customization.CustomizationAddView.as_view(), name="Customization"),

   path('categoryobject', Customization.CategoryDetail.as_view(), name="Category"),
   path('store_filter', StoreFilter.StoreFilterView.as_view(), name="StoreFilter"),
   path('store_filter/<int:pk>', StoreFilter.GetSingleStoreFilterView.as_view(), name="GetSingleStoreFilterView"),
   path('price_range', PriceRange.PriceFilter.as_view(), name="PriceRange"),
   path('navigation', Navigation.NavigationView.as_view(), name="NavigationView"),
   path('navigation/<int:pk>', Navigation.NavigationDetailView.as_view(), name="NavigationDetailView"),

   path('blog_list', Blog.BlogListView.as_view(), name="BlogListView"),
   path('blog', Blog.BlogView.as_view(), name="BlogView"),
   path('blog/<int:pk>', Blog.BlogDetailView.as_view(), name="BlogDetailView"),
   path('update_blog_status', Blog.BlogStatusChange.as_view(), name="update_blog_status"),

   path('blog_category_list', BlogCategory.BlogCategoryListView.as_view(), name="blog_category_list"),
   path('blog_category', BlogCategory.BlogCategoryView.as_view(), name="blog_category"),
   path('blog_category/<int:pk>', BlogCategory.BlogCategoryDetailView.as_view(), name="blog_category"),
   # All Custom API methods
]


schema_view = get_schema_view(
   openapi.Info(
      title="CMS (Content Management System) APIs Documentation",
      default_version='v1',
      description="This Documentation contains all the CRUD operations API needed for the cms application",
      terms_of_service="https://www.alchemative.com/privacy-policy",
      contact=openapi.Contact(email="app-support@alchemative.net"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   patterns=[
      path('cms/', include(urlpatterns))
   ],
)


urlpatterns += [
   # API Documentation route. (We are using Django Rest Swagger to sync with our API)
   path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]