
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Option
from products.Serializers.OptionSerializer import OptionSerializer, OptionUpdateSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class OptionView(APIView):

    @swagger_auto_schema(responses={200: OptionSerializer}, request_body=OptionSerializer)
    def post(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
            if type(request_data['product']) is not int:
                raise Exception("Product type must be an integer")

            option = OptionSerializer(data=request_data)
            if option.is_valid(raise_exception=True):
                option.save()

                # Post Entry in Logs
                action_performed = request.user.username + " created new product option"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(option.data, status=200)
            else:
                return Response(option.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    @swagger_auto_schema(responses={200: OptionUpdateSerializer}, request_body=OptionUpdateSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
            obj_id = request.data["id"]

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                option = Option.objects.filter(id=obj_id, product__vendor_id=vendor_id).first()
            else:
                option = Option.objects.filter(id=obj_id).first()

            serializer = OptionUpdateSerializer(option, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update product Option"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class OptionDetailView(APIView):

    @swagger_auto_schema(responses={200: OptionSerializer(many=True)})
    def get(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                instance = Option.objects.filter(product_id=pk, product__vendor_id=vendor_id)
            else:
                instance = Option.objects.filter(product_id=pk)

        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = OptionSerializer(instance, many=True)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched product options"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)


