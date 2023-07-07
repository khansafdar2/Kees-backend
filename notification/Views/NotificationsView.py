
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from ecomm_app.pagination import StandardResultSetPagination
from notification.BussinessLogic.FirebaseNotification import BackgroundNotification
from notification.models import FirebaseNotification
from datetime import datetime
from notification.Serializers.NotificationSerializer import NotificationListSerializer, NotificationSerializer, \
    NotificationDetailSerializer
from authentication.BusinessLogic.ApiPermissions import AccessApi
from authentication.BusinessLogic.ActivityStream import SystemLogs
from rest_framework import exceptions


class NotificationListView(ListCreateAPIView):
    serializer_class = NotificationListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        try:
            access = AccessApi(self.request.user, "notifications")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            queryset = FirebaseNotification.objects.filter(deleted=False).order_by('-created_at')

            # Post Entry in Logs
            action_performed = self.request.user.username + " get list of notifications"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)
            return queryset

        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class NotificationView(APIView):
    def post(self, request):
        access = AccessApi(self.request.user, "notifications")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        is_send = request_data.pop('is_send')
        payment = NotificationSerializer(data=request_data)
        if payment.is_valid(raise_exception=True):
            payment.save()

            # Post Entry in Logs
            action_performed = self.request.user.username + " create notification"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            if is_send:
                notification_id = payment.data['id']
                BackgroundNotification.send_notification_in_background(self, notification_id)

            return Response(payment.data, status=200)
        else:
            return Response(payment.errors, status=422)

    def put(self, request):
        access = AccessApi(self.request.user, "notifications")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data
        is_send = request_data.pop('is_send')

        payment = FirebaseNotification.objects.filter(id=obj_id).first()
        serializer = NotificationSerializer(payment, data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = self.request.user.username + " update notification"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            if is_send:
                BackgroundNotification.send_notification_in_background(self, obj_id)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class NotificationDetailView(APIView):
    def get(self, request, pk):
        access = AccessApi(self.request.user, "notifications")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            instance = FirebaseNotification.objects.get(pk=pk, deleted=False)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = NotificationDetailSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single notification"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        access = AccessApi(self.request.user, "notifications")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            FirebaseNotification.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + " delete notification"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted Notification Successfully!"}, status=200)

