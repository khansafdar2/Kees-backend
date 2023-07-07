
from django.urls import path, include
from authentication.Views import \
    User, \
    SignIn, \
    ChangePassword, \
    RolePermissionApi, \
    ResendOTP, \
    VerifyOTP, \
    ForgotPassword, \
    EmailProvider, \
    MessageProvider, \
    UserInvitation, \
    TransferOwnership
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from authentication import views
from authentication.BusinessLogic import EmailSender

urlpatterns = [
    # User Management
    path('users', User.UserView.as_view()),
    path('users/<int:pk>', User.UserDetailView.as_view()),
    path('check_username_email', User.CheckUserNameEmail.as_view()),
    path('signin', SignIn.SignIn.as_view()),

    # User Invitation
    path('accept_invite', UserInvitation.AcceptInvitation),
    path('check_invite_status', UserInvitation.CheckInviteExpiry.as_view()),
    path('input_password', UserInvitation.InputPassword.as_view()),
    path('resend_invitation', UserInvitation.ResendInvitation.as_view()),

    # Password Manipulation
    path('change_password', ChangePassword.ChangePassword.as_view()),
    path('forgotPassword', ForgotPassword.ForgotPassword.as_view()),
    path('verify_code', ForgotPassword.VerifyCode.as_view()),
    path('reset_forgot_password', ForgotPassword.ResetPassword.as_view()),

    # Transfer Ownership
    path('transfer_ownership', TransferOwnership.TransferOwner.as_view()),

    # Two Factor authentication
    # path('resend_otp', ResendOTP.ResendOTP.as_view()),
    # path('verify_otp', VerifyOTP.VerifyOTP.as_view()),

    # SMS and Email Providers
    # path('sms_providers', MessageProvider.MessageProviderView.as_view()),
    # path('send_message', MessageProvider.SendCustomMessage.as_view()),
    # path('email_providers', EmailProvider.EmailProviderView.as_view()),
    # path('send_email', EmailProvider.SendCustomEmail.as_view()),

    # Role Permission
    # path('role_permissions', RolePermissionApi.RolePermissionView.as_view()),
    # path('permissions_list', RolePermissionApi.RolePermissionList.as_view()),
    # path('single_permission', RolePermissionApi.RolePermissionItem.as_view()),
    # path('get_user_role', User.UserRolePermission.as_view()),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Authentication APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the Authentication application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('authentication/', include(urlpatterns))
    ],
)

urlpatterns += [
    # API Documentation route. (We are using Django Rest Swagger to sync with our API)
    path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
