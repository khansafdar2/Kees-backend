
import csv
from rest_framework.response import Response
from rest_framework.views import APIView
from products.DataMigration.DataMigrationSerializers.CategoryDataMigrationSerializer import MainCategoryMigrateSerializer, \
    SubCategoryMigrateSerializer, SuperSubCategoryMigrateSerializer


def read_file(request):
    file = request.data['file']
    file = file.read().decode('utf-8').splitlines()
    csv_files = csv.DictReader(file)
    csv_file = [dict(i) for i in csv_files]
    return csv_file


class MainCategoryMigrateView(APIView):
    def post(self, request):
        csv_file = read_file(request)

        for i in csv_file:
            main_category = MainCategoryMigrateSerializer(data=i)
            if main_category.is_valid(raise_exception=True):
                main_category.save()
            else:
                return Response(main_category.errors, status=422)
        return Response({'Data inserted Successfully'}, status=200)


class SubCategoryMigrateView(APIView):
    def post(self, request):
        csv_file = read_file(request)
        for i in csv_file:
            sub_category = SubCategoryMigrateSerializer(data=i)
            if sub_category.is_valid(raise_exception=True):
                sub_category.save()
            else:
                return Response(sub_category.errors, status=422)
        return Response({'Data inserted Successfully'}, status=200)


class SuperSubCategoryMigrateView(APIView):
    def post(self, request):
        csv_file = read_file(request)
        for i in csv_file:
            super_sub_category = SuperSubCategoryMigrateSerializer(data=i)
            if super_sub_category.is_valid(raise_exception=True):
                super_sub_category.save()
            else:
                return Response(super_sub_category.errors, status=422)
        return Response({'Data inserted Successfully'}, status=200)
