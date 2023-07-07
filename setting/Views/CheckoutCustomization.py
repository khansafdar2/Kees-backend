
from rest_framework.response import Response
from rest_framework.views import APIView
from setting.models import CheckoutSetting
from setting.Serializers.CheckoutCustomizationSerializer import CheckoutCustomizationSerializer
from authentication.BusinessLogic.ApiPermissions import AccessApi
from authentication.BusinessLogic.ActivityStream import SystemLogs
from rest_framework import exceptions


class CheckoutCustomizationView(APIView):
    def get(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        query_set = CheckoutSetting.objects.filter(deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)

        serializer = CheckoutCustomizationSerializer(query_set)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get checkout customization"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return Response(serializer.data, status=200)

    def post(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        checkout_setting = CheckoutSetting.objects.filter(deleted=False).first()
        if checkout_setting:
            serializer = CheckoutCustomizationSerializer(checkout_setting, data=request_data)
        else:
            serializer = CheckoutCustomizationSerializer(data=request_data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # Post Entry in Logs
            action_performed = self.request.user.username + " create checkout customization"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)
