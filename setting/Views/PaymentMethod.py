
from rest_framework.response import Response
from rest_framework.views import APIView
from setting.models import PaymentMethod
from datetime import datetime
from setting.Serializers.PaymentMethodSerializer import PaymentSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ApiPermissions import AccessApi
from authentication.BusinessLogic.ActivityStream import SystemLogs
from rest_framework import exceptions


class PaymentMethodView(APIView):

    @swagger_auto_schema(responses={200: PaymentSerializer})
    def get(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        query_set = PaymentMethod.objects.filter(deleted=False)
        if not query_set:
            data = {}
            return Response(data, status=200)

        serializer = PaymentSerializer(query_set, many=True)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get list of payment methods"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: PaymentSerializer}, request_body=PaymentSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        payment = PaymentSerializer(data=request_data)
        if payment.is_valid(raise_exception=True):
            payment.save()

            # Post Entry in Logs
            action_performed = self.request.user.username + " create payment method"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(payment.data, status=200)
        else:
            return Response(payment.errors, status=422)

    @swagger_auto_schema(responses={200: PaymentSerializer}, request_body=PaymentSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data

        payment = PaymentMethod.objects.filter(id=obj_id).first()
        serializer = PaymentSerializer(payment, data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = self.request.user.username + " update payment method"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class PaymentMethodDetailView(APIView):
    @swagger_auto_schema(responses={200: PaymentSerializer}, request_body=PaymentSerializer)
    def get(self, request, pk):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            instance = PaymentMethod.objects.get(pk=pk, deleted=False)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = PaymentSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single payment method"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            PaymentMethod.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + " delete payment method"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted shipping Successfully!"}, status=200)

