
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from cms.models import StoreFilter
from cms.Serializers.StoreFilterSerializer import StoreFilterSerializer
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions
from datetime import datetime


class StoreFilterView(APIView):
    @swagger_auto_schema(responses={200: StoreFilterSerializer(many=True)})
    def get(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = StoreFilter.objects.filter(deleted=False).order_by('id')
        if not query_set:
            data = []
            return Response(data, status=200)

        serializer = StoreFilterSerializer(query_set, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: StoreFilterSerializer}, request_body=StoreFilterSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        StoreFilter.objects.all().delete()
        store_filter = StoreFilterSerializer(data=request_data, many=True)

        if store_filter.is_valid(raise_exception=True):
            store_filter.save()
            return Response(store_filter.data, status=200)
        else:
            return Response(store_filter.errors, status=422)

    @swagger_auto_schema(responses={200: StoreFilterSerializer}, request_body=StoreFilterSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data

        if obj_id is None:
            serializer = StoreFilterSerializer(data=request_data)
        else:
            store_filter = StoreFilter.objects.filter(id=obj_id).first()
            serializer = StoreFilterSerializer(store_filter, data=request_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    @swagger_auto_schema(responses={200: StoreFilterSerializer}, request_body=StoreFilterSerializer)
    def delete(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = request.data["id"]
        if obj_id is not None:
            try:
                StoreFilter.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Filter ID not found in request"}, status=404)

        return Response({"detail": "Deleted Filter Successfully!"}, status=200)


class GetSingleStoreFilterView(APIView):
    def get(self, request, pk):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = StoreFilter.objects.filter(id=pk).first()
        if not query_set:
            data = {}
            return Response(data, status=200)

        serializer = StoreFilterSerializer(query_set)
        return Response(serializer.data, status=200)

