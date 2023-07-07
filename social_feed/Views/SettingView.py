
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from social_feed.models import Setting
from rest_framework import exceptions
from social_feed.Serializers.SettingSerializer import SettingSerializer


# Setting CRUD
class SettingView(APIView):
    def get(self, request):
        access = AccessApi(self.request.user, "socialfeed")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access this api")

        setting = Setting.objects.filter(deleted=False).first()
        if not setting:
            return Response({"detail": "app setting not found"}, status=404)

        serializer = SettingSerializer(setting)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get social feed setting"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return Response(serializer.data, status=200)

    def post(self, request):
        access = AccessApi(self.request.user, "socialfeed")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        setting = Setting.objects.filter(deleted=False).first()
        if setting:
            serializer = SettingSerializer(setting, data=request_data)
        else:
            serializer = SettingSerializer(data=request_data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # Post Entry in Logs
            action_performed = self.request.user.username + " create/update social feed setting"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)
