from rest_framework.response import Response
from rest_framework.views import APIView
from setting.models import Tax
from setting.Serializers.TaxSerializer import TaxSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class TaxView(APIView):

    @swagger_auto_schema(responses={200: TaxSerializer})
    def get(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = Tax.objects.filter(deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)

        serializer = TaxSerializer(query_set)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: TaxSerializer}, request_body=TaxSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        tax = TaxSerializer(data=request_data)
        try:
            tax = Tax.objects.get(deleted=False)
            return Response({"detail": "Tax cannot be recreated"}, status=404)
        except Exception as e:
            print(e)
            if tax.is_valid(raise_exception=True):
                tax.save()
                return Response(tax.data, status=200)
            else:
                return Response(tax.errors, status=422)

    @swagger_auto_schema(responses={200: TaxSerializer}, request_body=TaxSerializer)
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
            serializer = TaxSerializer(data=request_data)
        else:
            tax = Tax.objects.filter(id=obj_id).first()
            serializer = TaxSerializer(tax, data=request_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)
