
import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from cms.Serializers.CustomizationSerializer import CustomizationSerializer
from cms.models import Customization
from products.models import MainCategory, SubCategory, SuperSubCategory, CategoryHandle
from products.Serializers.CategorySerializer import MainCategorySerializer, SubCategorySerializer,\
    SuperSubCategorySerializer


class HomePageView(APIView):
    def get(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        customization = Customization.objects.filter(deleted=False).first()
        if not customization:
            data = {}
            return Response(data, status=200)

        serializer = CustomizationSerializer(customization)
        response_data = {
            "homepage": serializer.data['homepage_json'],
            "allowed_sections": serializer.data['allowed_sections']
        }
        return Response(response_data, status=200)


class HeaderView(APIView):
    def get(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        customization = Customization.objects.filter(deleted=False).first()
        if not customization:
            data = {}
            return Response(data, status=200)

        serializer = CustomizationSerializer(customization)
        response_data = {
            "header": serializer.data['header']
        }
        return Response(response_data, status=200)


class FooterView(APIView):
    def get(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        customization = Customization.objects.filter(deleted=False).first()
        if not customization:
            data = {}
            return Response(data, status=200)

        serializer = CustomizationSerializer(customization)
        response_data = {
            "footer": serializer.data['footer']
        }
        return Response(response_data, status=200)


class CustomizationAddView(APIView):
    def post(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = json.loads(request.body)
        customization = Customization.objects.filter(deleted=False).first()

        if customization:
            if 'homepage' in request_data.keys():
                Customization.objects.update(homepage_json=request_data['homepage'])

            if 'header' in request_data.keys():
                Customization.objects.update(header=request_data['header'])

            if 'footer' in request_data.keys():
                Customization.objects.update(footer=request_data['footer'])

            return Response("successfully updated", status=200)
        else:
            if 'header' in request_data.keys():
                home_page = Customization(header=request_data['header'])
                home_page.save()

            if 'footer' in request_data.keys():
                home_page = Customization(header=request_data['footer'])
                home_page.save()

            if 'homepage' in request_data.keys():
                home_page = Customization(homepage_json=request_data['homepage'])
                home_page.save()

            return Response("Successfully Created", status=200)


class CategoryDetail(APIView):
    def get(self, request):
        try:
            access = AccessApi(self.request.user, "customization")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            try:
                category_handle = self.request.GET.get('category_handle', None)
                if category_handle is not None:
                    category = CategoryHandle.objects.filter(name=category_handle).first()
                    category_type = category.category_type

                    if category_type == 'main_category':
                        category = MainCategory.objects.filter(handle=category_handle, is_active=True, deleted=False).first()
                        serializer = MainCategorySerializer(category)
                    elif category_type == 'sub_category':
                        category = SubCategory.objects.filter(handle=category_handle, is_active=True, deleted=False).first()
                        serializer = SubCategorySerializer(category)
                    elif category_type == 'super_sub_category':
                        category = SuperSubCategory.objects.filter(handle=category_handle, is_active=True, deleted=False).first()
                        serializer = SuperSubCategorySerializer(category)
                    else:
                        serializer = False

            except Exception as e:
                return Response({"detail": str(e)}, status=404)

            if serializer:
                data = serializer.data
                data['type'] = category_type
            else:
                data = {}

            # Post Entry in Logs
            action_performed = request.user.username + " fetched category from handle for homepage setting"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(data)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)
