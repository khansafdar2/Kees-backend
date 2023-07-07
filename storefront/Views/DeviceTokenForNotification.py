from rest_framework.response import Response
from rest_framework.views import APIView

from notification.models import FirebaseDeviceToken


class DeviceTokenForNotification(APIView):
    def post(self, request):
        try:
            request_data = request.data
            token = request_data['token']
            existing_token = FirebaseDeviceToken.objects.filter(device_token=token).first()
            if existing_token:
                return Response({'detail': 'Token already exist'}, status=200)
            new_token = FirebaseDeviceToken.objects.create(device_token=token)
            new_token.save()
            return Response(True, status=200)
        except Exception as e:
            print(e)
            return Response(False, status=422)

    def delete(self, request):
        try:
            request_data = request.data
            token = request_data['token']
            new_token = FirebaseDeviceToken.objects.get(device_token=token).delete()
            new_token.save()
            return Response(True, status=200)
        except Exception as e:
            print(e)
            return Response(False, status=422)
