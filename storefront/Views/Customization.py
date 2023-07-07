
from rest_framework.response import Response
from rest_framework.views import APIView
from cms.models import Customization
from storefront.Serializers.CustomizationSerializer import NewsletterSerializer, HomePageSerializer, HeaderSerializer,\
    FooterSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from storefront.BussinessLogic.CheckDomain import check_domain


class NewsletterView(APIView):
    @swagger_auto_schema(responses={200: NewsletterSerializer}, request_body=NewsletterSerializer)
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        newsletter = NewsletterSerializer(data=request_data)

        if newsletter.is_valid(raise_exception=True):
            newsletter.save()
            return Response(newsletter.data, status=200)
        else:
            return Response(newsletter.errors, status=422)


class HomePageView(APIView):
    @swagger_auto_schema(responses={200: HomePageSerializer}, request_body=HomePageSerializer)
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        home_page = Customization.objects.filter(deleted=False).first()
        if not home_page:
            data = {}
            return Response(data, status=200)
        serializer = HomePageSerializer(home_page)
        return Response(serializer.data, status=200)


class HeaderView(APIView):
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        home_page = Customization.objects.filter(deleted=False).first()
        if not home_page:
            data = {}
            return Response(data, status=200)
        serializer = HeaderSerializer(home_page)
        return Response(serializer.data, status=200)


class FooterView(APIView):
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        home_page = Customization.objects.filter(deleted=False).first()
        if not home_page:
            data = {}
            return Response(data, status=200)
        serializer = FooterSerializer(home_page)
        return Response(serializer.data, status=200)
