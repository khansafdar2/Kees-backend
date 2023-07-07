
from rest_framework.views import APIView
from authentication.Serializer.ForgotPasswordSerializer import ForgotPasswordSerialzier, ChangeForgotPasswordSerializer, VerifyCodeSerializer
from rest_framework.response import Response
import random, datetime
from authentication.models import User
from django.conf import settings
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.EmailSender import send_email, email_templates
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema

from setting.models import StoreInformation


class ForgotPassword(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(responses={200: ForgotPasswordSerialzier}, request_body=ForgotPasswordSerialzier)
    def post(self, request):
        url = settings.CLIENT_URL
        serializer = ForgotPasswordSerialzier(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        now = datetime.datetime.now()
        code = str(random.randint(1000, 9999))
        user.forgot_password_code = code
        user.forgot_password_code_is_valid = True
        user.save()

        try:
            store = StoreInformation.objects.get(deleted=False)
        except Exception as e:
            print(e)
            return Response({'detail': 'Store not exist'}, status=404)

        email_content = {'user_name': f"{user.first_name} {user.last_name}", 'code': code}
        email_template = email_templates(template_name='user_forgot_password', email_content=email_content)

        send_email(
            email_subject=f"{store.store_name} User Forgot Password",
            to_email=user.email,
            email_template=email_template
        )

        # Post Entry in Logs
        action_performed = user.username + " send forgot password request"
        SystemLogs.post_logs(self, request, user, action_performed)

        return Response()


class ResetPassword(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(responses={200: ChangeForgotPasswordSerializer}, request_body=ChangeForgotPasswordSerializer)
    def post(self, request):
        serializer = ChangeForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(forgot_password_code=serializer.validated_data["code"]).first()
        if user is not None:
            user.set_password(request.data["password"])
            user.forgot_password_code = None
            user.forgot_password_code_is_valid = False
            user.save()

            # Post Entry in Logs
            action_performed = user.username + " password reset by using forgot password option"
            SystemLogs.post_logs(self, request, user, action_performed)

            content = {"detail": "Password Changed"}
            return Response(content)
        else:
            content = {"detail": "Code not found or invalid"}
            return Response(content, status=404)


class VerifyCode(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(responses={200: VerifyCodeSerializer}, request_body=VerifyCodeSerializer)
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(forgot_password_code=serializer.validated_data["code"],
                                   forgot_password_code_is_valid=True).first()
        if user is not None:

            # Post Entry in Logs
            action_performed = user.username + " password code verified by pin"
            SystemLogs.post_logs(self, request, user, action_performed)

            return Response({"valid": True}, status=200)
        else:
            content = {"valid": False}
            return Response(content, status=404)

