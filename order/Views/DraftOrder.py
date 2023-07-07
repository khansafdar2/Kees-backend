
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from order.models import Checkout, LineItems, Order, DraftOrder
from order.Serializers.DraftOrderSerializer import AdminOrderAddSerializer, DraftOrderDetailSerializer, DraftOrderListSerializer
from drf_yasg.utils import swagger_auto_schema
from ecomm_app.pagination import StandardResultSetPagination
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class DraftOrderListView(ListCreateAPIView):
    serializer_class = DraftOrderListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "order")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this api")

            search = self.request.GET.get('search', None)

            queryset = DraftOrder.objects.all()
            if search is not None:
                queryset = queryset.filter(name__icontains=search)

            # Post Entry in Logs
            action_performed = self.request.user.username + " get list of draft orders"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return queryset
        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class DraftOrderView(APIView):
    @swagger_auto_schema(responses={200: AdminOrderAddSerializer}, request_body=AdminOrderAddSerializer)
    def post(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "order")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this api")

            request_data = request.data
            serializer = AdminOrderAddSerializer(data=request_data)
            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = self.request.user.username + " create draft order"
                SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    @swagger_auto_schema(responses={200: AdminOrderAddSerializer}, request_body=AdminOrderAddSerializer)
    def put(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "order")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this api")

            request_data = request.data
            draft = DraftOrder.objects.filter(id=request_data['id']).first()
            serializer = AdminOrderAddSerializer(draft, data=request_data)
            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = self.request.user.username + " update draft order"
                SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class DraftOrderDetailView(APIView):
    @swagger_auto_schema(responses={200: DraftOrderDetailSerializer}, request_body=DraftOrderDetailSerializer)
    def get(self, request, pk):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "order")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this api")

            draft = DraftOrder.objects.filter(id=pk).first()
            if not draft:
                data = {}
                return Response(data, status=200)

            serializer = DraftOrderDetailSerializer(draft)

            # Post Entry in Logs
            action_performed = self.request.user.username + " get single draft order detail"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=422)
