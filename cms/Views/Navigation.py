
import json
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from cms.models import Navigation
from cms.Serializers.NavigationSerializer import NavigationSerializer, NavigationListSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ApiPermissions import AccessApi
from authentication.BusinessLogic.ActivityStream import SystemLogs
from rest_framework import exceptions


class NavigationView(APIView):
    def get(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = Navigation.objects.filter(deleted=False)
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = NavigationListSerializer(query_set, many=True)

        # system Logs
        action_performed = request.user.username + " fetched navigations list"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    def post(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            serializer = NavigationSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            # system Logs
            action_performed = request.user.username + " Create navigation"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response("Navigation created successfully", status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    @swagger_auto_schema(responses={200: NavigationSerializer}, request_body=NavigationSerializer)
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

            navigation = Navigation.objects.filter(id=object_id, deleted=False).first()
            serializer = NavigationSerializer(navigation, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            # system Logs
            action_performed = request.user.username + " Update navigation" + str(object_id)
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": "Navigation Updated Successfully"}, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class NavigationDetailView(APIView):
    @swagger_auto_schema(responses={200: NavigationSerializer(many=True)})
    def get(self, request, pk):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = Navigation.objects.filter(id=pk, deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)

        serializer = NavigationSerializer(query_set)

        # system Logs
        action_performed = request.user.username + " Get navigation" + str(pk)
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = pk
        if obj_id is not None:
            try:
                Navigation.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())

                # system Logs
                action_performed = request.user.username + " Delete navigation" + str(pk)
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response({"detail": "Deleted Navigation Successfully!"}, status=200)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Navigation ID not found in request"}, status=404)
