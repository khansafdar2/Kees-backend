
from products.models import Brand
from rest_framework.response import Response
from products.Serializers.BrandSerializer import BrandDetailSerializer
from rest_framework.generics import ListCreateAPIView
from ecomm_app.pagination import StandardResultSetPagination
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from storefront.BussinessLogic.CheckDomain import check_domain


class StorefrontBrandView(ListCreateAPIView):
    serializer_class = BrandDetailSerializer
    pagination_class = StandardResultSetPagination

    @swagger_auto_schema(responses={200: BrandDetailSerializer(many=True)})
    def get_queryset(self):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        search = self.request.GET.get('search', None)
        try:
            if search is not None:
                queryset = Brand.objects.filter(name__icontains=search, deleted=False)
            else:
                queryset = Brand.objects.filter(deleted=False)

            if queryset is None:
                data = []
                return Response(data, status=200)
            return queryset
        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))
