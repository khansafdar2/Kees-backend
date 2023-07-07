
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from ecomm_app.pagination import StandardResultSetPagination
from shipping.Serializers.ZoneSerializer import ZoneListSerializer, AddZoneSerializer, ZoneDetailSerializer, \
    ShippingZoneListSerializer, VendorZoneListSerializer
from shipping.models import Zone, Shipping
from django.db.models import Q


class DefaultZoneListView(ListCreateAPIView):
    serializer_class = ShippingZoneListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access configuration")

        shipping_id = self.request.GET.get('shipping_id', None)
        if shipping_id is not None:
            shipping = list(set(Shipping.objects.filter((~Q(id=shipping_id)), deleted=False, default=True, is_active=True).values_list('zone_id', flat=True)))
        else:
            shipping = list(set(Shipping.objects.filter(deleted=False, default=True, is_active=True).values_list('zone_id', flat=True)))

        queryset = Zone.objects.filter(is_active=True, deleted=False).exclude(id__in=shipping)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get list of all default Zones"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return queryset


class CustomZoneListView(ListCreateAPIView):
    serializer_class = ShippingZoneListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access configuration")

        shipping_id = self.request.GET.get('shipping_id', None)
        vendor_id = self.request.GET.get('vendor', None)

        # if shipping_id is not None:
        #     shipping = list(set(Shipping.objects.filter((~Q(id=shipping_id, vendor_id=vendor_id)), deleted=False, default=False, is_active=True).values_list('zone_id',flat=True)))
        # else:
        #     shipping = list(set(Shipping.objects.filter((~Q(vendor_id=vendor_id)), deleted=False, default=False, is_active=True).values_list('zone_id',flat=True)))
        #
        # queryset = Zone.objects.filter(is_active=True, deleted=False).exclude(id__in=shipping)
        queryset = Zone.objects.filter(is_active=True, deleted=False)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get list of custom Zones"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return queryset


class ZoneListView(ListCreateAPIView):
    serializer_class = ZoneListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access configuration")

        queryset = Zone.objects.filter(deleted=False)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get list of all Zones"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return queryset


class ZoneView(APIView):

    @swagger_auto_schema(responses={200: AddZoneSerializer}, request_body=AddZoneSerializer)
    def post(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "configuration")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access configuration")

            request_data = request.data
            serializer = AddZoneSerializer(data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + "Add new zone"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

    @swagger_auto_schema(responses={200: AddZoneSerializer}, request_body=AddZoneSerializer)
    def put(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "configuration")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access configuration")

            request_data = request.data
            obj_id = request_data["id"]
            zone = Zone.objects.filter(id=obj_id).first()
            serializer = AddZoneSerializer(zone, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + f"updated zone with title: {zone.title}"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class ZoneDetailView(APIView):
    @swagger_auto_schema(responses={200: ZoneDetailSerializer})
    def get(self, request, pk):

        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access configuration")
        try:
            instance = Zone.objects.get(pk=pk)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = ZoneDetailSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + f" fetched single zone with title: {instance.title}"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access configuration")

        obj_id = pk
        if obj_id is not None:
            try:
                shipping = Shipping.objects.filter(zone_id=obj_id, deleted=False)
                if shipping:
                    return Response({"detail": "Zone is attach to shipping, please de-attach and then delete zone"}, status=404)

                Zone.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
                return Response({"detail": "Deleted Zone Successfully!"}, status=200)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Zone ID not found in request"}, status=404)


class VendorZoneListView(APIView):
    def get(self, request, pk):
        try:
            instance = Zone.objects.get(pk=pk)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = VendorZoneListSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + f" fetched single zone with title: {instance.title}"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)
