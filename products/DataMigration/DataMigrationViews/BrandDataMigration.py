
import csv
from rest_framework.response import Response
from rest_framework.views import APIView
from products.DataMigration.DataMigrationSerializers.BrandDataMigrationSerializer import BrandMigrationSerializer
from products.DataMigration.BusinessLogic.CsvReader import read_file


def read_file(request):
    file = request.data['file']
    file = file.read().decode('latin1').splitlines()
    csv_files = csv.DictReader(file)
    csv_file = [dict(i) for i in csv_files]
    return csv_file


class BrandMigrationView(APIView):
    def post(self, request):
        csv_file = read_file(request)

        for i in csv_file:
            brand = BrandMigrationSerializer(data=i)
            if brand.is_valid(raise_exception=True):
                brand.save()
            else:
                return Response(brand.errors, status=422)
        return Response({'Data inserted Successfully'}, status=200)
