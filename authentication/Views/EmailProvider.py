
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import EmailProvider
from authentication.BusinessLogic.EmailService import EmailServiceProvider
from authentication.Serializer.EmailProviderSerializer import EmailProviderSerializer, EmailProviderDeleteSerializer
from authentication.BusinessLogic.ActivityStream import SystemLogs
from drf_yasg.utils import swagger_auto_schema


# Email Provider CRUD
class EmailProviderView(APIView):
    @swagger_auto_schema(responses={200: EmailProviderSerializer(many=True)})
    def get(self, request):

        # Post Entry in Logs
        action_performed = request.user.username + " fetch all email providers "
        SystemLogs.post_logs(self, request, request.user, action_performed)

        providers = EmailProvider.objects.all().values()
        serializer = EmailProviderSerializer(providers, many=True)
        return Response({'email_providers': serializer.data}, status=200)

    @swagger_auto_schema(responses={200: EmailProviderSerializer}, request_body=EmailProviderSerializer)
    def post(self, request):
        request_data = request.data
        serializer = EmailProviderSerializer(data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " create email provider " + serializer.provider_type
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    @swagger_auto_schema(responses={200: EmailProviderSerializer}, request_body=EmailProviderSerializer)
    def put(self, request):
        obj_id = request.data.get("id", None)
        request_data = request.data
        if obj_id is None:
            serializer = EmailProviderSerializer(data=request_data)
        else:
            provider = EmailProvider.objects.filter(id=obj_id).first()
            serializer = EmailProviderSerializer(provider, data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update email provider " + provider.provider_type
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    @swagger_auto_schema(responses={200: EmailProviderDeleteSerializer}, request_body=EmailProviderDeleteSerializer)
    def delete(self, request):
        obj_id = request.data.get('id', None)
        provider = EmailProvider.objects.get(id=obj_id)

        # Post Entry in Logs
        action_performed = request.user.username + " delete email provider " + provider.provider_type
        SystemLogs.post_logs(self, request, request.user, action_performed)

        provider.delete()
        return Response({"detail": "Deleted"})


# Custom Email API for Test Connection
class SendCustomEmail(APIView):
    def post(self, request):
        obj_id = request.data.get("id", None)
        provider = EmailProvider.objects.filter(id=obj_id).first()

        # Post Entry in Logs
        action_performed = request.user.username + " send email"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        email_response = EmailServiceProvider.send_email(provider, request.data['email'].replace(" ", ""), request.data['email_subject'], request.data['email_body'], provider, None, request.META.get('REMOTE_ADDR'))
        return Response({"detail": "Email Successfully Send", "email_response": email_response}, status=200)
