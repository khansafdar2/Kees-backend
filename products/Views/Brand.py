
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from products.models import Brand, Product, Media
from products.Serializers.BrandSerializer import AddBrandSerializer, BrandDetailSerializer
from drf_yasg.utils import swagger_auto_schema
from ecomm_app.pagination import StandardResultSetPagination
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class BrandListView(ListAPIView):
    serializer_class = BrandDetailSerializer
    pagination_class = StandardResultSetPagination

    @swagger_auto_schema(responses={200: BrandDetailSerializer(many=True)})
    def get_queryset(self):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            column = self.request.GET.get('column', None)
            search = self.request.GET.get('search', None)

            queryset = Brand.objects.filter(deleted=False)
            if column is not None:
                if column == "name":
                    queryset = queryset.filter(name__icontains=search)

            if not queryset:
                data = []
                return Response(data, status=200)

            # Post Entry in Logs
            action_performed = self.request.user.username + " fetched all brands"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return queryset

        except Exception as e:
            raise exceptions.ParseError(str(e))


class BrandView(APIView):
    @swagger_auto_schema(responses={200: AddBrandSerializer}, request_body=AddBrandSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "products")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")
        try:
            request_data = request.data
            serializer = AddBrandSerializer(data=request_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                data = serializer.data
                if "image" in serializer.validated_data:
                    image = serializer.validated_data['image']
                else:
                    image = None
                data.update({
                    "image": image
                })

                # Post Entry in Logs
                action_performed = request.user.username + " created new brand"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    @swagger_auto_schema(responses={200: AddBrandSerializer}, request_body=AddBrandSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "products")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data
        if obj_id is None:
            serializer = AddBrandSerializer(data=request_data)
        else:
            brand = Brand.objects.filter(id=obj_id).first()
            serializer = AddBrandSerializer(brand, data=request_data)

        if serializer.is_valid():
            serializer.save()

            data = serializer.data
            if "image" in serializer.validated_data:
                image = serializer.validated_data['image']
            else:
                image = None
            data.update({
                "image": image
            })

            # Post Entry in Logs
            action_performed = request.user.username + " Update brand"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(data, status=200)
        else:
            return Response(serializer.errors, status=422)


class BrandDetailView(APIView):
    @swagger_auto_schema(responses={200: BrandDetailSerializer})
    def get(self, request, pk):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            try:
                brand = Brand.objects.get(pk=pk)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)

            serializer = BrandDetailSerializer(brand)

            # Post Entry in Logs
            action_performed = request.user.username + " fetched single brand"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    def delete(self, request, pk):
        access = AccessApi(self.request.user, "products")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = pk
        if obj_id is not None:
            try:
                brand = Brand.objects.get(id=obj_id)
                product = Product.objects.filter(product_brand=brand)
                for prod in product:
                    prod.product_brand = None
                    prod.save()
                Media.objects.filter(brand_id=brand.id).update(brand=None)
                Brand.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Brand ID not found in request"}, status=404)

        return Response({"detail": "Deleted brand Successfully!"}, status=200)
