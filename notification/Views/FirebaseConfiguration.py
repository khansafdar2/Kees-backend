
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.ApiPermissions import AccessApi
from notification.Serializers.FirebaseSettingsSerializer import FirebaseSettingsSerializer
from notification.models import FirebaseSettings


class FirebaseConfigurationView(APIView):
    def get(self, request):
        access = AccessApi(self.request.user, "notifications")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = FirebaseSettings.objects.filter(deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)

        serializer = FirebaseSettingsSerializer(query_set)
        return Response(serializer.data, status=200)

    def post(self, request):
        try:
            access = AccessApi(self.request.user, "notifications")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            request_data = request.data
            firebase_settings = FirebaseSettings.objects.filter(deleted=False).first()

            if firebase_settings:
                serializer = FirebaseSettingsSerializer(firebase_settings, data=request_data)
            else:
                serializer = FirebaseSettingsSerializer(data=request_data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            return Response({e}, status=400)
