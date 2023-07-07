
import jsonfield
from authentication.models import TimeStampedModel
from django.db import models


class FirebaseSettings(TimeStampedModel):
    project_name = models.CharField(blank=True, null=True, max_length=200)
    project_id = models.CharField(blank=True, null=True, max_length=200)
    project_number = models.CharField(blank=True, null=True, max_length=200)
    web_api_key = models.CharField(blank=True, null=True, max_length=200)
    server_key = models.CharField(blank=True, null=True, max_length=200)
    sender_id = models.CharField(blank=True, null=True, max_length=200)
    vapid_key = models.CharField(blank=True, null=True, max_length=200)
    credentials_json = jsonfield.JSONField(blank=True, null=True)
    auth_domain = models.CharField(blank=True, null=True, max_length=200)
    storage_bucket = models.CharField(blank=True, null=True, max_length=200)
    app_id = models.CharField(blank=True, null=True, max_length=200)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class FirebaseNotification(TimeStampedModel):
    message_title = models.TextField(blank=True, null=True)
    message_description = models.TextField(blank=True, null=True)
    message_image_url = models.TextField(blank=True, null=True)
    redirect_url = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class FirebaseNotificationHistory(TimeStampedModel):
    firebase_notification = models.ForeignKey(FirebaseNotification,  on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class FirebaseDeviceToken(TimeStampedModel):
    device_token = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)
