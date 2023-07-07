
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from cms.models import Page
from cms.Serializers.PageSerializer import PageSerializer, PageDeleteSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class PagesView(APIView):

    @swagger_auto_schema(responses={200: PageSerializer(many=True)})
    def get(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = Page.objects.filter(deleted=False)
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = PageSerializer(query_set, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: PageSerializer}, request_body=PageSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        page = PageSerializer(data=request_data)
        try:
            handle = request_data['title'].replace(' ', '-')
            request_data['handle'] = handle.lower()
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)
        if page.is_valid(raise_exception=True):
            page.save()
            return Response(page.data, status=200)
        else:
            return Response(page.errors, status=422)

    @swagger_auto_schema(responses={200: PageSerializer}, request_body=PageSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data

        if obj_id is None:
            serializer = PageSerializer(data=request_data)
        else:
            page = Page.objects.filter(id=obj_id).first()
            serializer = PageSerializer(page, data=request_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class PagesDetailView(APIView):

    @swagger_auto_schema(responses={200: PageSerializer(many=True)})
    def get(self, request, pk):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = Page.objects.filter(id=pk, deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = PageSerializer(query_set)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: PageDeleteSerializer}, request_body=PageDeleteSerializer)
    def delete(self, request, pk):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = pk
        if obj_id is not None:
            try:
                Page.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Page ID not found in request"}, status=404)

        return Response({"detail": "Deleted Page Successfully!"}, status=200)
