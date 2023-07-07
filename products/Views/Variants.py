
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Variant, InventoryHistory, Product, Option
from products.BusinessLogic.HideOutOfStock import hide_stock
from products.Serializers.VariantSerializer import \
    VariantDetailSerializer, \
    VariantAddSerializer, \
    UpdateVariantSerializer, \
    BulkDeleteVariantsSerializer, \
    GetInventorySerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class VariantView(APIView):

    @swagger_auto_schema(responses={200: VariantAddSerializer}, request_body=VariantAddSerializer)
    def post(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            request_data = request.data
            request_data['user'] = self.request.user
            variant = VariantAddSerializer(data=request_data)
            if variant.is_valid(raise_exception=True):
                variant.save()

                # Post Entry in Logs
                action_performed = request.user.username + " created variant"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(variant.data, status=200)
            else:
                return Response(variant.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    @swagger_auto_schema(responses={200: UpdateVariantSerializer}, request_body=UpdateVariantSerializer)
    def put(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            request_data = request.data
            obj_id = request.data["id"]
            request_data['user'] = self.request.user

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                variant = Variant.objects.filter(id=obj_id, product__vendor_id=vendor_id, deleted=False).first()
            else:
                variant = Variant.objects.filter(id=obj_id, deleted=False).first()

            serializer = UpdateVariantSerializer(variant, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update variants"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class VariantDetailView(APIView):

    @swagger_auto_schema(responses={200: VariantDetailSerializer})
    def get(self, request, pk):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                instance = Variant.objects.get(pk=pk, product__vendor_id=vendor_id, deleted=False)
            else:
                instance = Variant.objects.get(pk=pk, deleted=False)

            serializer = VariantDetailSerializer(instance)

            # Post Entry in Logs
            action_performed = request.user.username + " fetched single variant detail"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=404)

    def delete(self, request, pk):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            obj_id = pk

            if obj_id is not None:
                if self.request.user.is_vendor:
                    vendor_id = self.request.user.vendor_id
                    product = Product.objects.filter(product_variant__id=obj_id, vendor_id=vendor_id).first()
                else:
                    product = Product.objects.filter(product_variant__id=obj_id).first()

                Variant.objects.filter(id=obj_id, deleted=False).update(deleted=True, sku=None, deleted_at=datetime.now(), product=None, legacy_product=product.id)

                # hide out of stock
                hide_stock(product)

                if len(Variant.objects.filter(product_id=product.id, deleted=False)) == 0:
                    first_variant = Variant.objects.filter(id=obj_id).first()
                    data = CreateDefaultVariant(first_variant, product.id)
                    product.has_variants = False
                    product.save()
                    # Post Entry in Logs
                    action_performed = request.user.username + " deleted variant"
                    SystemLogs.post_logs(self, request, request.user, action_performed)

                    return Response(data, status=200)
            else:
                return Response({"detail": "Variant ID not found in request"}, status=404)
            # Post Entry in Logs
            action_performed = request.user.username + " deleted variant"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": "Deleted Variant Successfully!"}, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class BulkDeleteVariants(APIView):
    @swagger_auto_schema(responses={200: BulkDeleteVariantsSerializer}, request_body=BulkDeleteVariantsSerializer)
    def post(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            request_data = request.data
            ids = request_data['ids']
            product_id = request_data["product"]

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                product = Product.objects.filter(product_variant__id=product_id, vendor_id=vendor_id).first()
            else:
                product = Product.objects.filter(product_variant__id=product_id).first()

            variants = Variant.objects.filter(product_id=product_id, deleted=False)
            if len(variants) == len(ids):
                first_variant = variants.first()
                data = CreateDefaultVariant(first_variant, product_id)
                product.has_variants = False
                product.save()
                # Post Entry in Logs
                variants.filter(id__in=ids).update(deleted=True, sku=None, deleted_at=datetime.now(), product=None,
                                                   legacy_product=product.id)
                action_performed = request.user.username + " deleted bulk variants"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(data, status=200)

            variants.filter(id__in=ids).update(deleted=True, sku=None, deleted_at=datetime.now(), product=None,
                                               legacy_product=product.id)

            # hide out of stock
            hide_stock(product)

            # Post Entry in Logs
            action_performed = request.user.username + " deleted bulk variants"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": "Deleted Variants Successfully"}, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


def CreateDefaultVariant(first_variant, product_id):
    try:
        default_variant = {
            "title": "Default Title",
            "price": first_variant.price,
            "sku": first_variant.sku,
            "position": 1,
            "compare_at_price": first_variant.compare_at_price,
            "option1": "Default Title",
            "option2": None,
            "option3": None,
            "taxable": first_variant.taxable,
            "barcode": first_variant.barcode,
            "weight": first_variant.weight,
            "inventory_quantity": first_variant.inventory_quantity,
            "old_inventory_quantity": first_variant.old_inventory_quantity
        }
        default_option = {
            "name": "Title",
            "position": 1,
            "values": "Default Title"
        }
        product = Product.objects.filter(id=product_id).first()
        Option.objects.filter(product=product).delete()
        Option.objects.create(product=product, **default_option)
        variant = Variant.objects.create(product=product, **default_variant)
        default_variant['id'] = variant.id
        data = {
            "variants": [default_variant],
            "options": [default_option]
        }

        # hide out of stock
        hide_stock(product)

        return data
    except Exception as e:
        raise Exception(e)


class GetInventoryView(APIView):

    @swagger_auto_schema(responses={200: GetInventorySerializer(many=True)})
    def get(self, request, pk):
        access = AccessApi(self.request.user, "products")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            query_set = InventoryHistory.objects.filter(variant_id=pk)
            if not query_set:
                data = {}
                return Response(data, status=200)

            serializer = GetInventorySerializer(query_set, many=True)

            # Post Entry in Logs
            action_performed = request.user.username + " fetched inventory tracking for variant"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=404)
