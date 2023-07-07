
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from datetime import datetime
from vendor.models import Vendor


class User(AbstractUser):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)
    token = models.CharField(max_length=200, blank=True, null=True)
    api_token_expired = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    forgot_password_code = models.CharField(max_length=100, null=True, blank=True)
    forgot_password_code_is_valid = models.BooleanField(null=True, blank=True)
    email_2fa = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=100, null=True, blank=True)
    phone_2fa = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=False)
    phone_otp = models.CharField(max_length=100, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    is_vendor = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['deleted', 'id']),
        ]


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class UserInvitation(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_invitation")
    key = models.CharField(blank=True, null=True, max_length=200)
    accepted = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class ActivityStream(TimeStampedModel):
    username = models.TextField(blank=True, null=True)
    role_name = models.TextField(blank=True, null=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    action_performed = models.TextField(blank=True, null=True)
    previous_data = models.TextField(blank=True, null=True)
    updated_data = models.TextField(blank=True, null=True)
    ip_address = models.CharField(max_length=200, blank=True, null=True)


class RolePermission(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_permission", null=True)
    dashboard = models.BooleanField(default=False)
    theme = models.BooleanField(default=False)
    products = models.BooleanField(default=False)
    orders = models.BooleanField(default=False)
    customer = models.BooleanField(default=False)
    discounts = models.BooleanField(default=False)
    configuration = models.BooleanField(default=False)
    customization = models.BooleanField(default=False)
    vendor = models.BooleanField(default=False)
    approvals = models.BooleanField(default=False)
    featured_apps = models.BooleanField(default=False)
    notifications = models.BooleanField(default=False)
    socialfeed = models.BooleanField(default=False)

    # 2nd level product module
    product_list = models.BooleanField(default=False)
    product_groups = models.BooleanField(default=False)
    collections = models.BooleanField(default=False)
    categories = models.BooleanField(default=False)
    brands = models.BooleanField(default=False)

    # 2nd level customization module
    homepage = models.BooleanField(default=False)
    static_pages = models.BooleanField(default=False)
    header = models.BooleanField(default=False)
    footer = models.BooleanField(default=False)
    navigation = models.BooleanField(default=False)
    filters = models.BooleanField(default=False)
    blog = models.BooleanField(default=False)

    # 2nd level discount module
    main_discounts = models.BooleanField(default=False)
    coupons = models.BooleanField(default=False)

    # 2nd level configuration module
    store_setting = models.BooleanField(default=False)
    user_management = models.BooleanField(default=False)
    loyalty = models.BooleanField(default=False)
    shipping_regions = models.BooleanField(default=False)
    shipping_methods = models.BooleanField(default=False)
    checkout_setting = models.BooleanField(default=False)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class MessageProvider(TimeStampedModel):
    provider_type = models.CharField(max_length=250, blank=True, null=True)
    provider_msisdn = models.CharField(max_length=250, blank=True, null=True)
    provider_username = models.CharField(max_length=250, blank=True, null=True)
    provider_password = models.CharField(max_length=250, blank=True, null=True)
    provider_mask = models.CharField(max_length=250, blank=True, null=True)
    provider_sid = models.CharField(max_length=250, blank=True, null=True)
    message_dr = models.CharField(max_length=250, blank=True, null=True)
    message_lang = models.CharField(max_length=250, blank=True, null=True)
    message_type = models.CharField(max_length=250, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class MessageLogs(TimeStampedModel):
    message = models.TextField(blank=True, null=True)
    number = models.CharField(max_length=250, blank=True, null=True)
    provider = models.CharField(max_length=250, blank=True, null=True)
    mask = models.CharField(max_length=250, blank=True, null=True)
    ip_address = models.CharField(max_length=250, blank=True, null=True)
    message_status = models.BooleanField(default=False)
    message_response = models.TextField(blank=True, null=True)


class EmailProvider(TimeStampedModel):
    provider_type = models.CharField(max_length=250, blank=True, null=True)
    api_key = models.TextField(blank=True, null=True)
    from_email = models.TextField(blank=True, null=True)
    smtp_host = models.CharField(max_length=255, blank=True, null=True)
    smtp_port = models.IntegerField(blank=True, null=True)
    smtp_password = models.CharField(max_length=255, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class EmailLogs(TimeStampedModel):
    email_body = models.TextField(blank=True, null=True)
    to_address = models.CharField(max_length=250, blank=True, null=True)
    provider = models.CharField(max_length=250, blank=True, null=True)
    from_address = models.CharField(max_length=250, blank=True, null=True)
    ip_address = models.CharField(max_length=250, blank=True, null=True)
    response_status = models.BooleanField(default=False)
    response_message = models.TextField(blank=True, null=True)


class UserLastLogin(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_last_login')
    ip_address = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['id', 'user']),
        ]


class EmailTemplates(TimeStampedModel):
    title = models.CharField(max_length=200, blank=True, null=True)
    template = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]

