from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from cms.models import Page
from storefront.Serializers.StaticPageSerializer import PageSerializer
from drf_yasg.utils import swagger_auto_schema
from storefront.BussinessLogic.CheckDomain import check_domain
from rest_framework import exceptions


class StaticPagesView(APIView):

    @swagger_auto_schema(responses={200: PageSerializer(many=True)})
    def get(self, request, slug):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = Page.objects.filter(handle=slug, publish_status=True, deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = PageSerializer(query_set)
        return Response(serializer.data, status=200)
