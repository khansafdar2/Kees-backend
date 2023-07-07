
from rest_framework.response import Response
from rest_framework.views import APIView
from products.DataMigration.DataMigrationSerializers.VendorDataMigrationSerializer import VendorMigrationSerializer
from products.DataMigration.BusinessLogic.CsvReader import read_file


class VendorDataMigrateView(APIView):
    def post(self, request):
        csv_file = read_file(request)

        for i in csv_file:
            vendor = VendorMigrationSerializer(data=i)
            if vendor.is_valid(raise_exception=True):
                vendor.save()
            else:
                return Response(vendor.errors, status=422)
        return Response({'Data inserted Successfully'}, status=200)
