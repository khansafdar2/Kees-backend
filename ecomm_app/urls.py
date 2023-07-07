from django.contrib import admin
from django.db import models
from django.urls import path
from django.conf.urls import include
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication
from cms.views import index
from discount.BusinessLogic.ApplyDiscount import apply_discount
from discount.BusinessLogic.DiscountStatus import discount_status_change
from discount.BusinessLogic.Scheduler import scheduler_start
from scripts.view import ScriptView
from social_feed.BusinessLogic.FeedGenerationListener import generate_feed
from storefront.SearchCustomLookup import Search

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('cms/', include('cms.urls')),
    path('authentication/', include('authentication.urls')),
    path('setting/', include('setting.urls')),
    path('crm/', include('crm.urls')),
    path('products/', include('products.urls')),
    path('vendors/', include('vendor.urls')),
    path('storefront/', include('storefront.urls')),
    path('discount/', include('discount.urls')),
    path('order/', include('order.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('paymentgateway/', include('paymentgateway.urls')),
    path('shipping/', include('shipping.urls')),
    path('notification/', include('notification.urls')),
    path('socialfeed/', include('social_feed.urls')),
    path('script', neglect_authentication(ScriptView)),
]

scheduler_start(apply_discount, 300)
scheduler_start(discount_status_change, 120)
scheduler_start(generate_feed, 3600)
