from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from social_feed.Views import FeedView, SettingView
from rest_framework import permissions

urlpatterns = [
    # Social Media Feed Default Setting
    path('settings', SettingView.SettingView.as_view(), name='feed_setting'),

    path('feed_list', FeedView.FeedListView.as_view(), name='feed_list'),
    path('feed', FeedView.FeedView.as_view(), name='feed'),
    path('feed/<int:pk>', FeedView.FeedDetailView.as_view(), name='FeedDetailView'),

    # path('feed_xml', FeedView.ExportFeed.as_view(), name='feed_xml'),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Socal Media Feed APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the Sizechart application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('social_feed/', include(urlpatterns))
    ],
)

urlpatterns += [
    # API Documentation route. (We are using Django Rest Swagger to sync with our API)
    path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
