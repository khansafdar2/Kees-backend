from datetime import datetime
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from cms.models import Blog
from cms.Serializers.BlogSerializer import BlogListSerializer, BlogSerializer, BlogStatusChangeSerializer
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions
from ecomm_app.pagination import StandardResultSetPagination
from storefront.BussinessLogic.CheckDomain import check_domain


class BlogListView(ListAPIView):
    serializer_class = BlogListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        access = AccessApi(self.request.user, "blog")
        access_domain = check_domain(self.request)
        if not access or access_domain:
            raise exceptions.ParseError("This user does not have permission to this Api")

        queryset = Blog.objects.filter(is_deleted=False)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get list of blog sections"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return queryset


class BlogView(APIView):
    def post(self, request):
        access = AccessApi(self.request.user, "blog")
        access_domain = check_domain(self.request)
        if not access or access_domain:
            raise exceptions.ParseError("This user does not have permission to this Api")

        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " created blog section"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=422)

    def put(self, request):
        access = AccessApi(self.request.user, "blog")
        access_domain = check_domain(self.request)
        if not access or access_domain:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "Id not found in data!"}, status=422)

        request_data = request.data

        blog = Blog.objects.filter(id=obj_id).first()
        serializer = BlogSerializer(blog, data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + f"updated blog section {obj_id}"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class BlogDetailView(APIView):
    def get(self, request, pk):
        try:
            access = AccessApi(self.request.user, "blog")
            access_domain = check_domain(self.request)
            if not access or access_domain:
                raise exceptions.ParseError("This user does not have permission to this Api")

            blog = Blog.objects.get(id=pk, is_deleted=False)

        except Exception as e:
            return Response({"detail": str(e)}, status=422)

        serializer = BlogSerializer(blog)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single blog section detail"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        access = AccessApi(self.request.user, "blog")
        access_domain = check_domain(self.request)
        if not access or access_domain:
            raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = pk
        if obj_id is not None:
            try:
                Blog.objects.filter(id=obj_id).update(is_deleted=True, deleted_at=datetime.now())
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Blog ID not found in request"}, status=422)

        return Response({"detail": "Deleted Blog Successfully!"}, status=200)


class BlogStatusChange(APIView):
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "blog")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        serializer = BlogStatusChangeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update blog status"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)
