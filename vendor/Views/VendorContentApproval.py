import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from vendor.Serializers.VendorContentSerializer import VendorContentListSerializer, UpdateApprovalDataStatusSerializer
from vendor.models import DataApproval
from rest_framework.generics import ListCreateAPIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from ecomm_app.pagination import StandardResultSetPagination
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class VendorContentListView(ListCreateAPIView):
    serializer_class = VendorContentListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        access = AccessApi(self.request.user, "approvals")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access approvals")

        status = self.request.GET.get('status')
        vendor = self.request.GET.get('vendor')

        queryset = DataApproval.objects.filter(deleted=False).order_by('-id')

        if status:
            queryset = queryset.filter(status=status)
        if vendor:
            queryset = queryset.filter(vendor_id=vendor)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get list of Vendors approval content"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return queryset


class VendorContentStatusChangeView(APIView):
    def put(self, request):
        access = AccessApi(self.request.user, "approvals")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access approvals")

        try:
            request_data = request.data
            obj_id = request_data["id"]

            request_data['action_perform_by'] = request.user.username
            request_data['action_perform_at'] = datetime.datetime.now()

            queryset = DataApproval.objects.filter(id=obj_id).first()
            serializer = UpdateApprovalDataStatusSerializer(queryset, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update vendor approval data status"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)