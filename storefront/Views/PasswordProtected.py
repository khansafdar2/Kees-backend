
from rest_framework.response import Response
from rest_framework.views import APIView
from cms.models import Preferences
from storefront.Serializers.PasswordProtectedSerializer import PasswordCheckerSerializer
from drf_yasg.utils import swagger_auto_schema
from cms.Serializers.PreferenceSerializer import PreferenceSerializer
from storefront.BussinessLogic.CheckDomain import check_domain
from rest_framework import exceptions


class ProtectedPasswordView(APIView):
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = Preferences.objects.filter(deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = PreferenceSerializer(query_set)
        return Response(serializer.data, status=200)


class PasswordCheckerView(APIView):

    @swagger_auto_schema(responses={200: PasswordCheckerSerializer}, request_body=PasswordCheckerSerializer)
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        serializer = PasswordCheckerSerializer(data=request.data)

        if serializer.is_valid():
            return Response({"match": True}, status=200)
        else:
            return Response({"match": False}, status=422)

