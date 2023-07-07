
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from storefront.BussinessLogic.CheckDomain import check_domain
from vendor.models import Vendor
from rest_framework import exceptions
from ecomm_app.pagination import StandardResultSetPagination
from rest_framework.generics import ListCreateAPIView
from storefront.Serializers.StorefrontVendorSerializer import VendorListSerializer
from storefront.BussinessLogic.CheckDomain import check_domain
from rest_framework import exceptions


class VendorListView(ListCreateAPIView):
    serializer_class = VendorListSerializer
    pagination_class = StandardResultSetPagination

    @swagger_auto_schema(responses={200: VendorListSerializer})
    def get_queryset(self):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        search = self.request.GET.get('search', None)
        try:
            queryset = Vendor.objects.filter(status='Approved', is_active=True, deleted=False)
            if search is not None:
                queryset = queryset.filter(name__icontains=search)

            if not queryset:
                data = []
                return Response(data, status=200)
            return queryset
        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))
