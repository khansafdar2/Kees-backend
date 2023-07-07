
import csv

from django.db.models import Q
from rest_framework import exceptions
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from ecomm_app.pagination import StandardResultSetPagination
from setting.Serializers.LocationsSerializer import CountryListSerializer, CityListSerializer, RegionListSerializer
from setting.models import Region, Country, City
from authentication.BusinessLogic.ApiPermissions import AccessApi
from authentication.BusinessLogic.ActivityStream import SystemLogs
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime

from shipping.models import Zone


class RegionListView(ListCreateAPIView):
    serializer_class = RegionListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            region = Region.objects.filter(deleted=False)

            # Post Entry in Logs
            action_performed = self.request.user.username + " fetched Region list"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return region

        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class RegionView(APIView):
    @swagger_auto_schema(responses={200: RegionListSerializer}, request_body=RegionListSerializer)
    def post(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        serializer = RegionListSerializer(data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " created region"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    @swagger_auto_schema(responses={200: RegionListSerializer}, request_body=RegionListSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data
        region = Region.objects.filter(id=obj_id, deleted=False).first()
        serializer = RegionListSerializer(region, data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # System logs
            action_performed = request.user.username + " update region"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class RegionDetailView(APIView):
    @swagger_auto_schema(responses={200: RegionListSerializer})
    def get(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            region = Region.objects.get(id=pk, deleted=False)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = RegionListSerializer(region)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single region"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: RegionListSerializer}, request_body=RegionListSerializer)
    def delete(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            Region.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + " delete Region"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted Region Successfully!"}, status=200)


class CountryListView(ListCreateAPIView):
    serializer_class = CountryListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            region_id = self.request.GET.get('region_id')
            query_set = Country.objects.filter(region_id=region_id, deleted=False)

            # system logs
            action_performed = self.request.user.username + "fetch country"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return query_set

        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class CountryView(APIView):
    @swagger_auto_schema(responses={200: CountryListSerializer}, request_body=CountryListSerializer)
    def post(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        serializer = CountryListSerializer(data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " created country"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    @swagger_auto_schema(responses={200: CountryListSerializer}, request_body=CountryListSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data
        country = Country.objects.get(id=obj_id, deleted=False)
        serializer = CountryListSerializer(country, data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # system logs
            action_performed = request.user.username + " update country"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class CountryDetailView(APIView):
    @swagger_auto_schema(responses={200: CountryListSerializer})
    def get(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            country = Country.objects.get(id=pk, deleted=False)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = CountryListSerializer(country)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single country"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: CountryListSerializer}, request_body=CountryListSerializer)
    def delete(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            Country.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + " delete Country"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted Country Successfully!"}, status=200)


class CityListView(ListCreateAPIView):
    serializer_class = CityListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            country_id = self.request.GET.get('country_id')
            zone_id = self.request.GET.get('zone_id')
            city_listing = self.request.GET.get('listing', False)

            if not city_listing:
                if zone_id is not None:
                    city = list(set(Zone.objects.filter((~Q(id=zone_id)), deleted=False, is_active=True).values_list('city', flat=True)))
                else:
                    city = list(set(Zone.objects.filter(deleted=False, is_active=True).values_list('city', flat=True)))

                query_set = City.objects.filter(country_id=country_id, deleted=False).exclude(id__in=city)
            else:
                query_set = City.objects.filter(country_id=country_id, deleted=False)

            # system logs
            action_performed = self.request.user.username + " fetch city"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return query_set

        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class CityView(APIView):
    @swagger_auto_schema(responses={200: CityListSerializer}, request_body=CityListSerializer)
    def post(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        serializer = CityListSerializer(data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " created city"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)

    @swagger_auto_schema(responses={200: CityListSerializer}, request_body=CityListSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data
        city = City.objects.get(id=obj_id, deleted=False)
        serializer = CityListSerializer(city, data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # system logs
            action_performed = request.user.username + " update city"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class CityDetailView(APIView):
    @swagger_auto_schema(responses={200: CityListSerializer})
    def get(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            city = City.objects.get(id=pk, deleted=False)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = CityListSerializer(city)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single city"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: CityListSerializer}, request_body=CityListSerializer)
    def delete(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            City.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + " delete City"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted City Successfully!"}, status=200)


class LocationsImport(APIView):
    def post(self, request):
        try:
            file = request.data['file']
            file = file.read().decode('utf-8').splitlines()
            csv_files = csv.DictReader(file)
            csv_file = [dict(i) for i in csv_files]

            for row in csv_file:
                name = row['region']
                region = Region.objects.filter(name__iexact=name).first()
                if region:
                    Country.objects.create(name=row["name"], country_code=row["country-code"], region=region)
                else:
                    Region.objects.create(name=row["region"], is_active=True)
                    region = Region.objects.filter(name__iexact=name).first()

                    Country.objects.create(name=row["name"], country_code=row["country-code"], region=region)
            return Response({'detail': 'Inserted'}, status=200)
        except Exception as e:
            print(e)
            return Response("Failed to upload CSV", status=404)
