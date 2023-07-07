
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.Serializers.BlogSerializer import BlogCategorySerializer
from cms.models import Blog, BlogCategory
from storefront.Serializers.StorefrontBlogSerializer import BlogListSerializer, BlogDetailSerializer
from rest_framework import exceptions
from ecomm_app.pagination import StandardResultSetPagination
from storefront.BussinessLogic.CheckDomain import check_domain


class BlogListView(ListAPIView):
    serializer_class = BlogListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        access_domain = check_domain(self.request)
        if access_domain:
            raise exceptions.ParseError("This user does not have permission to this Api")

        blog_category = self.request.GET.get('category_id', None)
        if blog_category is not None:
            queryset = Blog.objects.filter(blog_category_id=blog_category, status='publish', is_active=True, is_deleted=False)
        else:
            queryset = Blog.objects.filter(status='publish', is_active=True, is_deleted=False)

        return queryset


class BlogDetailView(APIView):
    def get(self, request, slug):
        try:
            access_domain = check_domain(self.request)
            if access_domain:
                raise exceptions.ParseError("This user does not have permission to this Api")

            blog = Blog.objects.get(handle=slug, is_deleted=False)

        except Exception as e:
            return Response({"detail": str(e)}, status=422)

        serializer = BlogDetailSerializer(blog)

        return Response(serializer.data, status=200)


class BlogCategoryListView(APIView):
    def get(self, request):
        access_domain = check_domain(self.request)
        if access_domain:
            raise exceptions.ParseError("This user does not have permission to this Api")

        blog_category = BlogCategory.objects.filter(is_deleted=False, is_active=True)
        serializer = BlogCategorySerializer(blog_category, many=True)

        return Response(serializer.data, status=200)
