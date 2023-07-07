
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from cms.models import PriceRangeFilter, StoreFilter
from cms.Serializers.PriceRangeSerializer import PriceFilterSerializer
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions
from datetime import datetime


class PriceFilter(APIView):
    @swagger_auto_schema(responses={200: PriceFilterSerializer(many=True)})
    def get(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = PriceRangeFilter.objects.filter(deleted=False)
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = PriceFilterSerializer(query_set, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: PriceFilterSerializer}, request_body=PriceFilterSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            for price in request.data['price_range']:
                price_range = PriceFilterSerializer(data=price)
                if price_range.is_valid(raise_exception=True):
                    price_range.save()

            return Response({"detail": "Add price ranges successfully"}, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

    @swagger_auto_schema(responses={200: PriceFilterSerializer}, request_body=PriceFilterSerializer)
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
            serializer = PriceFilterSerializer(data=request_data)
        else:
            price = PriceRangeFilter.objects.filter(id=obj_id).first()
            serializer = PriceFilterSerializer(price, data=request_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    @swagger_auto_schema(responses={200: PriceFilterSerializer}, request_body=PriceFilterSerializer)
    def delete(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = request.data["id"]
        if obj_id is not None:
            try:
                PriceRangeFilter.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Price ID not found in request"}, status=404)

        return Response({"detail": "Deleted price range Successfully!"}, status=200)