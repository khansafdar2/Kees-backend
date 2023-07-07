import pytz
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from setting.models import StoreInformation
from setting.Serializers.StoreInfoSerializer import StoreInfoSerializer, StoreInfoDeleteSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class StoreInfoView(APIView):

    @swagger_auto_schema(responses={200: StoreInfoSerializer})
    def get(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = StoreInformation.objects.filter(deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)

        serializer = StoreInfoSerializer(query_set)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: StoreInfoSerializer}, request_body=StoreInfoSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        store = StoreInfoSerializer(data=request_data)
        try:
            store = StoreInformation.objects.get(deleted=False)
            return Response({"detail": "Store Information cannot be recreated"}, status=404)
        except Exception as e:
            print(e)
            if store.is_valid(raise_exception=True):
                # try:
                #     timezone.activate(pytz.timezone(request_data['time_zone']))
                # except Exception as e:
                #     print(e)
                #     return Response({"detail": str(e)}, status=400)
                store.save()
                return Response(store.data, status=200)
            else:
                return Response(store.errors, status=422)

    @swagger_auto_schema(responses={200: StoreInfoSerializer}, request_body=StoreInfoSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data

        if obj_id is None:
            serializer = StoreInfoSerializer(data=request_data)
        else:
            store = StoreInformation.objects.filter(id=obj_id).first()
            serializer = StoreInfoSerializer(store, data=request_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    @swagger_auto_schema(responses={200: StoreInfoDeleteSerializer}, request_body=StoreInfoDeleteSerializer)
    def delete(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = request.data["id"]
        if obj_id is not None:
            try:
                StoreInformation.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
            except Exception as e:
                print(e)
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Store ID not found in request"}, status=404)

        return Response({"detail": "Deleted Store Successfully!"}, status=200)


class TimeZone(APIView):
    @swagger_auto_schema(responses={200: StoreInfoSerializer})
    def get(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        data = pytz.all_timezones
        return Response(data, status=200)


