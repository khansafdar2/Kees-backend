
from rest_framework.response import Response
from rest_framework.views import APIView
from storefront.Serializers.StorefrontCategorySerializer import CategoriesListSerializer, MainSubCategoriesSerializer
from products.models import MainCategory, SubCategory
from drf_yasg.utils import swagger_auto_schema
from storefront.BussinessLogic.CheckDomain import check_domain
from rest_framework import exceptions


class CategoryView(APIView):
    @swagger_auto_schema(responses={200: CategoriesListSerializer})
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = MainCategory.objects.filter(is_active=True, deleted=False).order_by('position')
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = CategoriesListSerializer(query_set, many=True)
        return Response(serializer.data, status=200)


class SubCategoryView(APIView):
    @swagger_auto_schema(responses={200: MainSubCategoriesSerializer})
    def get(self, request, slug):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = MainCategory.objects.filter(handle=slug, is_active=True, deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = MainSubCategoriesSerializer(query_set)
        return Response(serializer.data, status=200)
