from storefront.Urls import \
    StorefrontAuthenticationUrls, \
    CustomerUrls, \
    CategoryUrls, \
    ProductUrls, \
    FilterUrls, \
    BrandUrls, \
    PromotionProductsUrls, \
    CustomizationUrls, \
    StaticPageUrls, \
    VendorUrls, \
    WalletUrls, \
    DeviceTokenForNotificationUrls, \
    ExposedUrls, \
    BlogUrls

urlpatterns = StorefrontAuthenticationUrls.urlpatterns
urlpatterns += CustomerUrls.urlpatterns
urlpatterns += CategoryUrls.urlpatterns
urlpatterns += ProductUrls.urlpatterns
urlpatterns += FilterUrls.urlpatterns
urlpatterns += BrandUrls.urlpatterns
urlpatterns += PromotionProductsUrls.urlpatterns
urlpatterns += CustomizationUrls.urlpatterns
urlpatterns += StaticPageUrls.urlpatterns
urlpatterns += VendorUrls.urlpatterns
urlpatterns += WalletUrls.urlpatterns
urlpatterns += DeviceTokenForNotificationUrls.urlpatterns
urlpatterns += ExposedUrls.urlpatterns
urlpatterns += BlogUrls.urlpatterns
