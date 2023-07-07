
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import MessageProvider
from authentication.BusinessLogic.MessageService import MessageServiceProvider
from authentication.Serializer.MessageProviderSerializer import MessageProviderSerializer, MessageProviderDeleteSerializer
from authentication.BusinessLogic.ActivityStream import SystemLogs
from drf_yasg.utils import swagger_auto_schema


# Message Provider CRUD
class MessageProviderView(APIView):

    @swagger_auto_schema(responses={200: MessageProviderSerializer(many=True)})
    def get(self, request):
        # Post Entry in Logs
        action_performed = request.user.username + " fetch all message providers "
        SystemLogs.post_logs(self, request, request.user, action_performed)

        providers = MessageProvider.objects.all().values()
        serializer = MessageProviderSerializer(providers, many=True)
        return Response({'message_providers': serializer.data}, status=200)

    @swagger_auto_schema(responses={200: MessageProviderSerializer}, request_body=MessageProviderSerializer)
    def post(self, request):
        request_data = request.data
        if request_data['provider_type'] == 'Telenor':
            request_data['provider_username'] = request_data['provider_msisdn']
        serializer = MessageProviderSerializer(data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " create message provider " + serializer.provider_type
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    @swagger_auto_schema(responses={200: MessageProviderSerializer}, request_body=MessageProviderSerializer)
    def put(self, request):
        obj_id = request.data.get("id", None)
        request_data = request.data
        if request_data['provider_type'] == 'Telenor':
            request_data['provider_username'] = request_data['provider_msisdn']
        if obj_id is None:
            serializer = MessageProviderSerializer(data=request_data)
        else:
            provider = MessageProvider.objects.filter(id=obj_id).first()
            serializer = MessageProviderSerializer(provider, data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update message provider " + provider.provider_type
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    @swagger_auto_schema(responses={200: MessageProviderDeleteSerializer}, request_body=MessageProviderDeleteSerializer)
    def delete(self, request):
        obj_id = request.data.get('id', None)
        provider = MessageProvider.objects.get(id=obj_id)

        # Post Entry in Logs
        action_performed = request.user.username + " delete message provider " + provider.provider_type
        SystemLogs.post_logs(self, request, request.user, action_performed)

        provider.delete()
        return Response({"detail": "Deleted"})


# Custom SMS API for Test Connection
class SendCustomMessage(APIView):
    def post(self, request):
        obj_id = request.data.get("id", None)
        provider = MessageProvider.objects.filter(id=obj_id).first()

        # Post Entry in Logs
        action_performed = request.user.username + " send sms"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        sms_response = MessageServiceProvider.send_message(provider, request.data['phone'].replace(" ", ""), request.data['message'], provider, None, request.META.get('REMOTE_ADDR'))
        return Response({"detail": "Message Successfully Send", "sms_response": sms_response}, status=200)
