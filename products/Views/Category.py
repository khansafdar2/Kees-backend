from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import \
    MainCategory, \
    SubCategory, \
    SuperSubCategory, \
    Collection, \
    Media, \
    MainCategoryMetaData, \
    SubCategoryMetaData, \
    SuperSubCategoryMetaData
from products.Serializers.CategorySerializer import \
    MainCategorySerializer, \
    MainCategoryAddUpdateSerializer, \
    MainCategoryDetailSerializer, \
    MainCategoriesListSerializer, \
    SubCategorySerializer, \
    SubCategoryAddUpdateSerializer, \
    SubCategoryDetailSerializer, \
    SubCategoriesListSerializer, \
    SuperSubCategorySerializer, \
    SuperSubCategoryAddUpdateSerializer, \
    SuperSubCategoryDetailSerializer, \
    SuperSubCategoriesListSerializer, \
    CategoryAvailabilityChangeSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class CategoryView(APIView):
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this api")

            data = {}
            query_set1 = MainCategory.objects.filter(deleted=False).order_by('position')
            query_set2 = SubCategory.objects.filter(deleted=False).order_by('position')
            query_set3 = SuperSubCategory.objects.filter(deleted=False).order_by('position')
            serializer1 = MainCategoriesListSerializer(query_set1, many=True)
            serializer2 = SubCategoriesListSerializer(query_set2, many=True)
            serializer3 = SuperSubCategoriesListSerializer(query_set3, many=True)
            data.update({
                "main_categories": serializer1.data,
                "sub_categories": serializer2.data,
                "super_sub_categories": serializer3.data
            })
            # Post Entry in Logs
            action_performed = request.user.username + " fetched all main categories"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(data, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=200)


class MainCategoryView(APIView):

    @swagger_auto_schema(responses={200: MainCategorySerializer(many=True)})
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            query_set = MainCategory.objects.filter(deleted=False).order_by('position')
            if not query_set:
                data = []
                return Response(data, status=200)
            serializer = MainCategorySerializer(query_set, many=True)

            # Post Entry in Logs
            action_performed = request.user.username + " fetched all main categories"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    @swagger_auto_schema(responses={200: MainCategoryAddUpdateSerializer}, request_body=MainCategoryAddUpdateSerializer)
    def post(self, request):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            request_data = request.data
            try:
                if type(request_data['meta_data']) is dict:
                    raise Exception("Meta Data must be an array of objects")
                if request_data['slug'] is None:
                    slug = request_data['name'].replace(' ', '-')
                    request_data['slug'] = slug.lower()
            except Exception as e:
                print(e)
                return Response({"detail": str(e)}, status=404)
            serializer = MainCategoryAddUpdateSerializer(data=request_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " created main category"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                data = serializer.data
                if "banner_image" in serializer.validated_data:
                    banner_image = serializer.validated_data['banner_image']
                else:
                    banner_image = None
                data.update({
                    "banner_image": banner_image
                })

                return Response(data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            return Response({"detail": str(e)}, status=200)

    @swagger_auto_schema(responses={200: MainCategoryAddUpdateSerializer}, request_body=MainCategoryAddUpdateSerializer)
    def put(self, request):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            try:
                obj_id = request.data["id"]
                if type(request.data['meta_data']) is dict:
                    raise Exception("Meta Data must be an array of objects")
            except Exception as e:
                print(e)
                return Response({"detail": str(e)}, status=400)

            request_data = request.data
            main_category = MainCategory.objects.filter(id=obj_id).first()
            serializer = MainCategoryAddUpdateSerializer(main_category, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update main category"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                data = serializer.data
                if "banner_image" in serializer.validated_data:
                    banner_image = serializer.validated_data['banner_image']
                else:
                    banner_image = None
                data.update({
                    "banner_image": banner_image
                })

                return Response(data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            return Response({"detail": str(e)}, status=200)


class MainCategoryDetail(APIView):

    @swagger_auto_schema(responses={200: MainCategoryDetailSerializer})
    def get(self, request, pk):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            instance = MainCategory.objects.get(pk=pk)
            serializer = MainCategoryDetailSerializer(instance)

            # Post Entry in Logs
            action_performed = request.user.username + " fetched single Main category"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    def delete(self, request, pk):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            obj_id = pk
            if obj_id is not None:
                try:
                    category = MainCategory.objects.get(id=obj_id)
                    collections = Collection.objects.filter(main_category=category)
                    for collection in collections:
                        collection.main_category.remove(category)
                    Media.objects.filter(main_category_id=category.id).update(main_category=None)
                    MainCategory.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
                    MainCategoryMetaData.objects.filter(id=obj_id).delete()
                except Exception as e:
                    return Response({"detail": str(e)}, status=404)
            else:
                return Response({"detail": "Category ID not found in request"}, status=404)

            return Response({"detail": "Deleted Category Successfully!"}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=200)


class SubCategoryView(APIView):

    @swagger_auto_schema(responses={200: SubCategorySerializer(many=True)})
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            if "main_category" not in request.GET:
                return Response({"detail": "main_category must be passed as request parameter"}, status=400)
            main_category = request.GET.get('main_category')
            query_set = SubCategory.objects.filter(main_category_id=main_category, deleted=False).order_by('position')
            if not query_set:
                data = []
                return Response(data, status=200)
            serializer = SubCategorySerializer(query_set, many=True)

            # Post Entry in Logs
            action_performed = request.user.username + " fetched all sub categories"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

    @swagger_auto_schema(responses={200: SubCategoryAddUpdateSerializer}, request_body=SubCategoryAddUpdateSerializer)
    def post(self, request):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            request_data = request.data
            print(request_data)
            if type(request_data['meta_data']) is dict:
                raise Exception("Meta Data must be an array of objects")
            if 'main_category' not in request_data and type(request_data['main_category']) is not int:
                raise Exception("Main Category invalid or not found in request!")
            if request_data['slug'] is None:
                slug = request_data['name'].replace(' ', '-')
                request_data['slug'] = slug.lower()
            serializer = SubCategoryAddUpdateSerializer(data=request_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " created sub category"
                SystemLogs.post_logs(self, request, request.user, action_performed)
                data = serializer.data
                if "banner_image" in serializer.validated_data:
                    banner_image = serializer.validated_data['banner_image']
                else:
                    banner_image = None
                data.update({
                    "banner_image": banner_image
                })
                return Response(data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

    @swagger_auto_schema(responses={200: SubCategoryAddUpdateSerializer}, request_body=SubCategoryAddUpdateSerializer)
    def put(self, request):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            obj_id = request.data["id"]
            if type(request.data['meta_data']) is dict:
                raise Exception("Meta Data must be an array of objects")
            if 'main_category' not in request.data and type(request.data['main_category']) is not int:
                raise Exception("Main Category invalid or not found in request!")

            request_data = request.data
            sub_category = SubCategory.objects.filter(id=obj_id).first()
            serializer = SubCategoryAddUpdateSerializer(sub_category, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update sub category"
                SystemLogs.post_logs(self, request, request.user, action_performed)
                data = serializer.data
                if "banner_image" in serializer.validated_data:
                    banner_image = serializer.validated_data['banner_image']
                else:
                    banner_image = None
                data.update({
                    "banner_image": banner_image
                })
                return Response(data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)


class SubCategoryDetail(APIView):

    @swagger_auto_schema(responses={200: SubCategoryDetailSerializer})
    def get(self, request, pk):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            instance = SubCategory.objects.get(pk=pk)
            serializer = SubCategoryDetailSerializer(instance)

            # Post Entry in Logs
            action_performed = request.user.username + " fetched single sub category"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    def delete(self, request, pk):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            obj_id = pk
            if obj_id is not None:
                try:
                    category = SubCategory.objects.get(id=obj_id)
                    collections = Collection.objects.filter(sub_category=category)
                    for collection in collections:
                        collection.sub_category.remove(category)
                    Media.objects.filter(sub_category_id=category.id).update(sub_category=None)
                    SubCategory.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
                    SubCategoryMetaData.objects.filter(id=obj_id).delete()
                except Exception as e:
                    return Response({"detail": str(e)}, status=404)
            else:
                return Response({"detail": "Category ID not found in request"}, status=404)

            return Response({"detail": "Deleted Category Successfully!"}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=200)


class SuperSubCategoryView(APIView):

    @swagger_auto_schema(responses={200: SuperSubCategorySerializer(many=True)})
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            if "sub_category" not in request.GET:
                return Response({"detail": "sub_category must be passed as request parameter"}, status=400)

            sub_category = request.GET.get('sub_category')
            query_set = SuperSubCategory.objects.filter(sub_category_id=sub_category, deleted=False).order_by('position')
            if not query_set:
                data = []
                return Response(data, status=200)
            serializer = SuperSubCategorySerializer(query_set, many=True)

            # Post Entry in Logs
            action_performed = request.user.username + " fetched all super sub categories"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

    @swagger_auto_schema(responses={200: SuperSubCategoryAddUpdateSerializer}, request_body=SuperSubCategoryAddUpdateSerializer)
    def post(self, request):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            request_data = request.data
            if type(request_data['meta_data']) is dict:
                raise Exception("Meta Data must be an array of objects")
            if 'sub_category' not in request_data and type(request_data['sub_category']) is not int:
                raise Exception("Sub Category invalid or not found in request!")
            if request_data['slug'] is None:
                slug = request_data['name'].replace(' ', '-')
                request_data['slug'] = slug.lower()
            serializer = SuperSubCategoryAddUpdateSerializer(data=request_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " created super sub category"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                data = serializer.data
                if "banner_image" in serializer.validated_data:
                    banner_image = serializer.validated_data['banner_image']
                else:
                    banner_image = None
                data.update({
                    "banner_image": banner_image
                })
                return Response(data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    @swagger_auto_schema(responses={200: SuperSubCategoryAddUpdateSerializer}, request_body=SuperSubCategoryAddUpdateSerializer)
    def put(self, request):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            obj_id = request.data["id"]
            if type(request.data['meta_data']) is dict:
                raise Exception("Meta Data must be an array of objects")
            if 'sub_category' not in request.data and type(request.data['sub_category']) is not int:
                raise Exception("Sub Category invalid or not found in request!")

            request_data = request.data
            super_sub_category = SuperSubCategory.objects.filter(id=obj_id).first()
            serializer = SuperSubCategoryAddUpdateSerializer(super_sub_category, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update super sub category"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                data = serializer.data
                if "banner_image" in serializer.validated_data:
                    banner_image = serializer.validated_data['banner_image']
                else:
                    banner_image = None
                data.update({
                    "banner_image": banner_image
                })
                return Response(data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class SuperSubCategoryDetail(APIView):

    @swagger_auto_schema(responses={200: SuperSubCategoryDetailSerializer})
    def get(self, request, pk):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            try:
                instance = SuperSubCategory.objects.get(pk=pk)
                serializer = SuperSubCategoryDetailSerializer(instance)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)

            data = serializer.data

            # Post Entry in Logs
            action_performed = request.user.username + " fetched single super sub category"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(data)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

    def delete(self, request, pk):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            obj_id = pk
            if obj_id is not None:
                try:
                    category = SuperSubCategory.objects.get(id=obj_id)
                    collections = Collection.objects.filter(super_sub_category=category)
                    for collection in collections:
                        collection.super_sub_category.remove(category)
                    Media.objects.filter(super_sub_category_id=category.id).update(super_sub_category=None)
                    SuperSubCategory.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
                    SuperSubCategoryMetaData.objects.filter(id=obj_id).delete()
                except Exception as e:
                    return Response({"detail": str(e)}, status=404)
            else:
                return Response({"detail": "Category ID not found in request"}, status=404)

            return Response({"detail": "Deleted Category Successfully!"}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=200)


class CategoryAvailabilityChange(APIView):

    @swagger_auto_schema(responses={200: CategoryAvailabilityChangeSerializer}, request_body=CategoryAvailabilityChangeSerializer)
    def put(self, request):
        try:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            request_data = request.data
            serializer = CategoryAvailabilityChangeSerializer(data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update category availability status"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response({"detail": True}, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class CategoryPosition(APIView):
    def put(self, request):
        access = AccessApi(self.request.user, "products")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        category_type = request_data["type"]
        category_data = request_data["category_data"]

        for i in category_data:
            if category_type == 'main_category':
                MainCategory.objects.filter(id=i["id"]).update(position=i["position"])
            elif category_type == 'sub_category':
                SubCategory.objects.filter(id=i["id"]).update(position=i["position"])
            elif category_type == 'super_sub_category':
                SuperSubCategory.objects.filter(id=i["id"]).update(position=i["position"])
            else:
                return Response({'detail': 'invalid category type'}, status=404)

        return Response({"Successfully Updated"}, status=200)
