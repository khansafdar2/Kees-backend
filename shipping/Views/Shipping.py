
from datetime import datetime
from django.db.models import Q
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import exceptions
from rest_framework.response import Response
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from ecomm_app.pagination import StandardResultSetPagination
from products.models import ProductGroup
from shipping.models import Shipping, Rule, ConditionalRate, Zone, Region, Country
from shipping.Serializers.ShippingSerializer import ShippingSerializer, ShippingDetailSerializer, \
    ShippingListSerializer, ShippingProductGroupSerializer


class ShippingView(APIView):
    def get(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        if self.request.user.is_vendor:
            vendor = self.request.user.vendor_id
            query_set = Shipping.objects.filter(vendor_id=vendor, deleted=False)
        else:
            query_set = Shipping.objects.filter(deleted=False)

        if not query_set:
            data = []
            return Response(data, status=200)
        serializer = ShippingListSerializer(query_set, many=True)

        data = {'default_shipping': [], 'custom_shipping': []}
        for shipping in serializer.data:
            if shipping['default']:
                data['default_shipping'].append(shipping)
            else:
                data['custom_shipping'].append(shipping)

        # Post Entry in Logs
        action_performed = self.request.user.username + " fetched all shipping"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return Response(data, status=200)

    def post(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
            serializer = ShippingSerializer(data=request_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                # Post Entry in Logs
                action_performed = self.request.user.username + " create shipping"
                SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

                return Response(serializer.data, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")
        try:
            request_data = request.data
            obj_id = request_data["id"]
            shipping = Shipping.objects.filter(id=obj_id).first()
            serializer = ShippingSerializer(shipping, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = self.request.user.username + " update shipping"
                SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class ShippingDetailView(APIView):
    def get(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = Shipping.objects.filter(id=pk, deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = ShippingDetailSerializer(query_set)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get shipping" + str(pk)
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = pk
        if obj_id is not None:
            try:
                ConditionalRate.objects.filter(rule__shipping_id=obj_id).update(deleted=True, deleted_at=datetime.now())
                Rule.objects.filter(shipping_id=obj_id).update(deleted=True, deleted_at=datetime.now())
                Shipping.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())

                # Post Entry in Logs
                action_performed = self.request.user.username + " delete shipping" + str(pk)
                SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

                return Response({"detail": "Deleted Shipping Successfully!"}, status=200)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Shipping ID not found in request"}, status=404)


class RuleView(APIView):
    def delete(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = pk
        if obj_id is not None:
            try:
                ConditionalRate.objects.filter(rule_id=obj_id).update(deleted=True, deleted_at=datetime.now())
                Rule.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())

                # Post Entry in Logs
                action_performed = self.request.user.username + " delete rule" + f'{pk}'
                SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

                return Response({"detail": "Deleted Rule Successfully!"}, status=200)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Rule ID not found in request"}, status=404)


class ConditionalRateView(APIView):
    def delete(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = pk
        if obj_id is not None:
            try:
                ConditionalRate.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())

                # Post Entry in Logs
                action_performed = self.request.user.username + " delete conditional rate" + f'{pk}'
                SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

                return Response({"detail": "Deleted Conditional Rate Successfully!"}, status=200)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Conditional Rate ID not found in request"}, status=404)


class ZoneCountView(APIView):
    def get(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        zones = Zone.objects.filter(deleted=False).count()
        if not zones:
            data = {}
            return Response(data, status=200)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get total zones count"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return Response(zones, status=200)


class ShippingProductGroupListView(ListCreateAPIView):
    serializer_class = ShippingProductGroupSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access configuration")

        vendor = self.request.GET.get('vendor', None)
        shipping_id = self.request.GET.get('shipping_id', None)
        zone_id = self.request.GET.get('zone_id')

        if shipping_id is not None:
            product_group_list = list(set(Shipping.objects.filter((~Q(id=shipping_id)), zone_id=zone_id, deleted=False, default=False, is_active=True).values_list('product_group', flat=True)))
        else:
            product_group_list = list(set(Shipping.objects.filter(zone_id=zone_id, deleted=False, default=False, is_active=True).values_list('product_group', flat=True)))

        queryset = ProductGroup.objects.filter(vendor_id=vendor, is_active=True, deleted=False).exclude(id__in=product_group_list)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get list of shipping product groups"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return queryset


class RegionCountView(APIView):
    def get(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        regions = Region.objects.filter(deleted=False).count()

        countries = Country.objects.filter(deleted=False).count()
        country = list(set(Zone.objects.filter(deleted=False, is_active=True).values_list('country', flat=True)))
        country_without_zone = Country.objects.filter(is_active=True, deleted=False).exclude(id__in=country).count()

        region = list(set(Zone.objects.filter(deleted=False, is_active=True).values_list('region', flat=True)))
        region_without_zone = Region.objects.filter(is_active=True, deleted=False).exclude(id__in=region).count()

        # Post Entry in Logs
        action_performed = self.request.user.username + " get total regions count and countries count"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)
        data = {
            "region": regions,
            "countries": countries,
            "countries_without_zone": country_without_zone,
            "region_without_zone": region_without_zone,
        }
        return Response(data, status=200)
