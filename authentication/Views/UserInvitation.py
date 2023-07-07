
from django.conf import settings
from django.shortcuts import HttpResponse
from authentication.models import UserInvitation, User, RolePermission
from authentication.BusinessLogic.EmailSender import send_email, email_templates
from datetime import timedelta, datetime
from drf_yasg.utils import swagger_auto_schema
from authentication.Serializer.UserInviteSerializer import InviteSerializer, PasswordSerializer
from authentication.Serializer.RolePermissionSerializer import RolePermissionSerializer
from authentication.Views.SignIn import dummy_permission, get_token
from rest_framework.permissions import AllowAny
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from setting.models import StoreInformation


@swagger_auto_schema(auto_schema=None)
def AcceptInvitation(request):
    try:
        key = request.GET.get('key')
        invitation = UserInvitation.objects.get(key=key)
        if invitation.expired:
            return HttpResponse("This invitation has been expired")
        key_expiry = CheckExpiry(key, invitation)
        if key_expiry["status"]:
            return HttpResponse(key_expiry["message"])
        invitation.accepted = True
        invitation.save()

        # Redirect to Change Password Page
        return HttpResponse("Invitation Accepted")
    except Exception as e:
        print(e)
        return HttpResponse(str(e))


# User Check if invite has expired or not with key signature
class ResendInvitation(APIView):
    def post(self, request):
        try:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            try:
                store = StoreInformation.objects.get(deleted=False)
            except Exception as e:
                print(e)
                return Response({'detail': 'Store not exist'}, status=404)

            user = User.objects.get(id=request.data['id'])
            if user.is_active:
                return Response({"detail": "User invitation already accepted"}, status=400)
            invitation = UserInvitation.objects.get(user=user)

            email_content = {'url': settings.CLIENT_URL, 'key': invitation.key}
            email_template = email_templates(template_name='user_invite', email_content=email_content)

            send_email(
                to_email=user.email,
                email_subject=f"{store.store_name} User Invitation",
                email_template=email_template
            )

            # Post Entry in Logs
            action_performed = request.user.username + " resend invite to " + user.username
            SystemLogs.post_logs(self, request, request.user, action_performed)
            return Response({"detail": "Invitation send successfully!"}, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


def CheckExpiry(key, invite):
    utc_now = datetime.now()
    # utc_now = utc_now.replace(tzinfo=pytz.utc)
    if invite.created_at < utc_now - timedelta(hours=24):
        UserInvitation.objects.filter(key=key).update(expired=True)
        return {
            "status": True,
            "message": "Invitation has been expired"
        }
    else:
        return {
            "status": False
        }


# User Check if invite has expired or not with key signature
class CheckInviteExpiry(APIView):
    permission_classes = (AllowAny,)
    @swagger_auto_schema(responses={200: InviteSerializer}, request_body=InviteSerializer)
    def post(self, request):
        try:
            key = request.data['key']
            invitation = UserInvitation.objects.get(key=key)
            if invitation.expired:
                return Response({"expired": True}, status=200)
            key_expiry = CheckExpiry(key, invitation)
            if key_expiry["status"]:
                return Response({"expired": True}, status=200)
            else:
                return Response({"expired": False}, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


# Set User Password
class InputPassword(APIView):
    permission_classes = (AllowAny,)
    @swagger_auto_schema(responses={200: PasswordSerializer}, request_body=PasswordSerializer)
    def post(self, request):
        try:
            key = request.data['key']
            invitation = UserInvitation.objects.get(key=key)
            if invitation.expired:
                return Response({"detail": "Invitation is expired!"}, status=403)
            user = User.objects.get(id=invitation.user.id)
            key_expiry = CheckExpiry(key, invitation)
            if key_expiry["status"]:
                return Response({"detail": "Invitation is expired!"}, status=403)
            else:
                serializer = PasswordSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user.set_password(serializer.validated_data['password'])
                user.is_active = True
                user.last_login = datetime.now()
                user.token = get_token(user.username)
                user.save()
                invitation.expired = True
                invitation.save()
                try:
                    role_permission = RolePermission.objects.filter(user_id=user.id).first()
                    serializer = RolePermissionSerializer(role_permission)
                    role_obj = serializer.data
                except Exception as e:
                    print(e)
                    role_obj = dummy_permission()
                user_obj = {
                    "id": user.id,
                    "token": user.token,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "is_vendor": user.is_vendor,
                    "permission": role_obj
                }
                return Response(user_obj, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)
