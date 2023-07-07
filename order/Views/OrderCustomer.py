
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from ecomm_app.pagination import StandardResultSetPagination
from crm.models import Customer
from django.db.models import Q
from order.Serializers.OrderCustomerSerializer import OrderCustomerListSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi


class OrderCustomerListView(APIView):
    @swagger_auto_schema(responses={200: OrderCustomerListSerializer}, request_body=OrderCustomerListSerializer)
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "customer")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this api")

            search = self.request.GET.get('search', None)
            if search is not None:
                queryset = Customer.objects.filter((Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search)), deleted=False)[:15]
                serializer = OrderCustomerListSerializer(queryset, many=True)

                # Post Entry in Logs
                action_performed = self.request.user.username + " get list of Customers"
                SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response({'detail': 'missing search parameter'}, status=404)

        except Exception as e:
            print(e)
            return Response(str(e), status=400)
