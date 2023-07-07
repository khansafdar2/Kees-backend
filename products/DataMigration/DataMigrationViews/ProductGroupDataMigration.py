import csv, os
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from products.Serializers.ProductSerializer import AddProductSerializer
from products.DataMigration.DataMigrationSerializers.ProductGroupMigrationSerializer import ProductGroupMigrationSerializer
from products.DataMigration.BusinessLogic.CsvReader import read_file


class ProductGroupMigrateView(APIView):
    def post(self, request):
        csv_file = read_file(request)

        for i in csv_file:
            product_group = ProductGroupMigrationSerializer(data=i)
            if product_group.is_valid(raise_exception=True):
                product_group.save()
            else:
                return Response(product_group.errors, status=422)
        return Response({'Data inserted Successfully'}, status=200)
