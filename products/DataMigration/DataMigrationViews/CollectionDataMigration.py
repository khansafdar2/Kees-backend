
import csv
from rest_framework.response import Response
from rest_framework.views import APIView
from products.DataMigration.DataMigrationSerializers.CollectionDataMigrationSerializer import CollectionMigrationSerializer


def read_file(request):
    file = request.data['file']
    file = file.read().decode('latin1').splitlines()
    csv_files = csv.DictReader(file)
    csv_file = [dict(i) for i in csv_files]
    return csv_file


class CollectionMigrationView(APIView):
    def post(self, request):
        csv_file = read_file(request)

        for i in csv_file:
            collection = CollectionMigrationSerializer(data=i)
            if collection.is_valid(raise_exception=True):
                collection.save()
            else:
                return Response(collection.errors, status=422)
        return Response({'Data inserted Successfully'}, status=200)
