
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from paymentgateway.models import GatewayCredentials
from paymentgateway.Serializers.GatewayCredentialsSerializer import GatewayCredentialsListSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ApiPermissions import AccessApi
from authentication.BusinessLogic.ActivityStream import SystemLogs
from rest_framework import exceptions


class GatewayCredentialsView(APIView):
    def get(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = GatewayCredentials.objects.filter(deleted=False)
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = GatewayCredentialsListSerializer(query_set, many=True)

        # system Logs
        action_performed = request.user.username + " fetched gateway credentials list"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    def post(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            serializer = GatewayCredentialsListSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            # system Logs
            action_performed = request.user.username + " Create gateway credentials"
            SystemLogs.post_logs(self, request, request.user, action_performed)
            return Response(serializer.data, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    @swagger_auto_schema(responses={200: GatewayCredentialsListSerializer},
                         request_body=GatewayCredentialsListSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            try:
                object_id = request.data["id"]
            except Exception as e:
                print(e)
                return Response({"detail": "ID not found in data!"}, status=400)

            navigation = GatewayCredentials.objects.filter(id=object_id, deleted=False).first()
            serializer = GatewayCredentialsListSerializer(navigation, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            # system Logs
            action_performed = request.user.username + " Update gateway credentials" + str(object_id)
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": "Gateway Credentials Updated Successfully"}, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class GatewayCredentialsDetailView(APIView):
    @swagger_auto_schema(responses={200: GatewayCredentialsListSerializer(many=True)})
    def get(self, request, pk):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = GatewayCredentials.objects.filter(id=pk, deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)

        serializer = GatewayCredentialsListSerializer(query_set)

        # system Logs
        action_performed = request.user.username + " Get Single Gateway Credentials" + str(pk)
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = pk
        if obj_id is not None:
            try:
                GatewayCredentials.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())

                # system Logs
                action_performed = request.user.username + " Delete Gateway Credentials" + str(pk)
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response({"detail": "Deleted Gateway Credentials Successfully!"}, status=200)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Gateway Credentials ID not found in request"}, status=404)
