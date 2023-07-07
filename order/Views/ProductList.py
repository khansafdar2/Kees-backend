
from rest_framework.generics import ListCreateAPIView
from ecomm_app.pagination import StandardResultSetPagination
from products.models import Product
from order.Serializers.ProductListSerializer import ProductListSerializer
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class ProductListView(ListCreateAPIView):
    serializer_class = ProductListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

                vendor_id = self.request.GET.get('vendor', None)
                if not vendor_id:
                    queryset = Product.objects.filter(deleted=False, is_active=True, status='Approved')
                else:
                    queryset = Product.objects.filter(vendor_id=vendor_id, deleted=False, is_active=True, status='Approved')

            else:
                vendor_id = self.request.user.vendor_id
                queryset = Product.objects.filter(vendor_id=vendor_id, deleted=False, is_active=True, status='Approved')

            search = self.request.GET.get('search', None)
            if search is not None:
                queryset = queryset.filter(title__icontains=search)

            # Post Entry in Logs
            action_performed = self.request.user.username + " get list of Products"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return queryset
        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))
