
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from notification.Views import FirebaseConfiguration, NotificationsView, SendNotifications

urlpatterns = [
    # Products Crud
    path('firebase_configuration', FirebaseConfiguration.FirebaseConfigurationView.as_view(), name="FirebaseConfigurationView"),

    # Notification Crud
    path('notifications_list', NotificationsView.NotificationListView.as_view(), name="NotificationListView"),
    path('notifications', NotificationsView.NotificationView.as_view(), name="NotificationView"),
    path('notifications/<int:pk>', NotificationsView.NotificationDetailView.as_view(), name="NotificationView"),

    # Send Notification
    path('send_notification', SendNotifications.NotificationSend.as_view(), name="NotificationSend"),

]

schema_view = get_schema_view(
    openapi.Info(
        title="Dashboard APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the Products application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('notification/', include(urlpatterns))
    ],
)


urlpatterns += [
   # API Documentation route. (We are using Django Rest Swagger to sync with our API)
   path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
