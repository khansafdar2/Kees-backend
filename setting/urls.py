
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from setting.Views import StoreInformation, Tax, PaymentMethod, Locations, Loyalty, CheckoutCustomization
from setting.BusinessLogic import SecureApi
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication

urlpatterns = [
   # All CMS CRUD APIs needed
   path('store_info', StoreInformation.StoreInfoView.as_view(), name="StoreInfoView"),
   path('tax', Tax.TaxView.as_view(), name="TaxView"),

   path('payment_method', PaymentMethod.PaymentMethodView.as_view(), name="PaymentView"),
   path('payment_method/<int:pk>', PaymentMethod.PaymentMethodDetailView.as_view(), name="PaymentDetailView"),

   # All Custom API methods
   path('timezones', StoreInformation.TimeZone.as_view(), name="TimeZones"),

   # Secured Apis
   path('secured_api', SecureApi.SecuredApis, name="SecuredApis"),

   path('locations_import', neglect_authentication(Locations.LocationsImport), name="location_import"),

   # Locations
   path('region_list', Locations.RegionListView.as_view(), name="Region_List"),
   path('region', Locations.RegionView.as_view(), name="Region"),
   path('region/<int:pk>', Locations.RegionDetailView.as_view(), name="RegionDetail"),

   # Country
   path('country_list', Locations.CountryListView.as_view(), name="Country_list"),
   path('country', Locations.CountryView.as_view(), name="Country"),
   path('country/<int:pk>', Locations.CountryDetailView.as_view(), name="CountryDetail"),

   # City
   path('city_list', Locations.CityListView.as_view(), name="City_list"),
   path('city', Locations.CityView.as_view(), name="City"),
   path('city/<int:pk>', Locations.CityDetailView.as_view(), name="City"),

   # Loyalty Setting
   path('setting', Loyalty.SettingView.as_view(), name="setting"),
   path('setting/<int:pk>', Loyalty.RuleDetailView.as_view(), name="RuleDetailView"),

   # Checkout Setting
   path('checkout_setting', CheckoutCustomization.CheckoutCustomizationView.as_view(), name="checkout_setting"),
]


schema_view = get_schema_view(
   openapi.Info(
      title="Settings APIs Documentation",
      default_version='v1',
      description="This Documentation contains all the CRUD operations API needed for the setting application",
      terms_of_service="https://www.alchemative.com/privacy-policy",
      contact=openapi.Contact(email="app-support@alchemative.net"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   patterns=[
      path('setting/', include(urlpatterns))
   ],
)


urlpatterns += [
   # API Documentation route. (We are using Django Rest Swagger to sync with our API)
   path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]