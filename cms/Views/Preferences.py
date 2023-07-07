
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from cms.models import Preferences
from cms.Serializers.PreferenceSerializer import PreferenceSerializer
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions
from storefront.BussinessLogic.CheckDomain import check_domain


class PreferencesView(APIView):
    def get(self, request):
        access_domain = check_domain(self.request)
        if access_domain:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = Preferences.objects.filter(deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)

        serializer = PreferenceSerializer(query_set)
        return Response(serializer.data, status=200)

    def post(self, request):
        access_domain = check_domain(self.request)
        if access_domain:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        preferences = Preferences.objects.filter(deleted=False).first()
        if preferences:
            serializer = PreferenceSerializer(preferences, data=request_data)
        else:
            serializer = PreferenceSerializer(data=request_data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # Post Entry in Logs
            action_performed = self.request.user.username + " create/update preferences"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)