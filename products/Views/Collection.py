
from datetime import datetime
from ecomm_app.pagination import StandardResultSetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from products.models import Collection, Product, Media
from products.Serializers.CollectionSerializer import \
    CollectionAddSerializer, \
    CollectionDetailSerializer, \
    CollectionStatusChangeSerializer, \
    CollectionListSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class CollectionListView(ListCreateAPIView):
    serializer_class = CollectionListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        global queryset
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor = self.request.GET.get('vendor', None)
            column = self.request.GET.get('column', None)
            search = self.request.GET.get('search', None)
            status = self.request.GET.get('status', None)
            approval_status = self.request.GET.get('approval_status', None)

            if self.request.user.is_vendor:
                vendor = self.request.user.vendor_id

            if vendor is None:
                queryset = Collection.objects.filter(deleted=False)
            else:
                queryset = Collection.objects.filter(deleted=False, vendor_id=vendor)

            if column is not None:
                if column == "title":
                    queryset = queryset.filter(title__icontains=search)

            if status is not None:
                if status.lower() == 'active':
                    queryset = queryset.filter(is_active=True)
                elif status.lower() == 'inactive':
                    queryset = queryset.filter(is_active=False)
                else:
                    raise exceptions.ParseError("Invalid status filter")

            if approval_status is not None:
                if approval_status.lower() == 'approved':
                    queryset = queryset.filter(status='Approved')
                elif approval_status.lower() == 'disapproved':
                    queryset = queryset.filter(status='Disapproved')
                else:
                    raise exceptions.ParseError("Invalid approval status filter")

            # Post Entry in Logs
            action_performed = self.request.user.username + " get list of Collections"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)
            return queryset

        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class CollectionView(APIView):

    @swagger_auto_schema(responses={200: CollectionAddSerializer}, request_body=CollectionAddSerializer)
    def post(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")
        else:
            request.data['vendor'] = self.request.user.vendor_id

        request_data = request.data
        try:
            if type(request_data['meta_data']) is dict:
                raise Exception("Meta Data must be an array of objects")

            banner_image = request_data['banner_image']
            slug = request_data['title'].replace(' ', '-')
            if request_data['slug'] == "":
                request_data['slug'] = slug.lower()
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

        collection = CollectionAddSerializer(data=request_data)
        if collection.is_valid(raise_exception=True):
            collection.save()

            data = collection.data
            if "banner_image" in collection.validated_data:
                banner_image = collection.validated_data['banner_image']
            else:
                banner_image = None
            data.update({
                "banner_image": banner_image
            })

            # Post Entry in Logs
            action_performed = request.user.username + " created collection"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(data, status=200)
        else:
            return Response(collection.errors, status=422)

    @swagger_auto_schema(responses={200: CollectionAddSerializer}, request_body=CollectionAddSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")
        else:
            request.data['vendor'] = self.request.user.vendor_id

        try:
            request_data = request.data
            obj_id = request_data["id"]
            if type(request_data['meta_data']) is dict:
                raise Exception("Meta Data must be an array of objects")
            if request_data['slug'] == "":
                request_data['slug'] = request_data['title'].replace(" ", "-").lower()

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                collection = Collection.objects.filter(id=obj_id, vendor_id=vendor_id).first()
            else:
                collection = Collection.objects.filter(id=obj_id).first()

            serializer = CollectionAddSerializer(collection, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update collection"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

    def delete(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            ids = request.GET.get('ids')
            ids = ids.split(',')
            for obj_id in ids:
                if self.request.user.is_vendor:
                    vendor_id = self.request.user.vendor_id
                    collection = Collection.objects.get(id=obj_id, vendor_id=vendor_id)
                else:
                    collection = Collection.objects.get(id=obj_id)

                product = Product.objects.filter(collection=collection)
                for prod in product:
                    prod.collection.remove(collection)
                Media.objects.filter(collection_id=collection.id).update(collection=None)
                Collection.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

        return Response({"detail": "Deleted Collection Successfully!"}, status=200)


class CollectionDetail(APIView):
    @swagger_auto_schema(responses={200: CollectionDetailSerializer})
    def get(self, request, pk):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                instance = Collection.objects.filter(id=pk, vendor_id=vendor_id, deleted=False).first()
            else:
                instance = Collection.objects.filter(id=pk, deleted=False).first()

            if not instance:
                data = {}
                return Response(data, status=200)
            serializer = CollectionDetailSerializer(instance)

            # Post Entry in Logs
            action_performed = request.user.username + " fetched single collection"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class CollectionStatusChange(APIView):
    @swagger_auto_schema(responses={200: CollectionStatusChangeSerializer}, request_body=CollectionStatusChangeSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

        request_data['user'] = self.request.user
        serializer = CollectionStatusChangeSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update collection status"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": True}, status=200)
        else:
            return Response(serializer.errors, status=422)


