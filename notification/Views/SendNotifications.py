from rest_framework.response import Response
from rest_framework.views import APIView
from notification.models import FirebaseNotification, FirebaseDeviceToken, FirebaseNotificationHistory
from notification.BussinessLogic.FirebaseNotification import send_web_push_notification, BackgroundNotification
from authentication.BusinessLogic.ApiPermissions import AccessApi
from authentication.BusinessLogic.ActivityStream import SystemLogs
from rest_framework import exceptions


class NotificationSend(APIView):
    def post(self, request):
        access = AccessApi(self.request.user, "notifications")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        notification = FirebaseNotification.objects.filter(id=request.data['id']).first()
        if notification:
            BackgroundNotification.send_notification_in_background(self, notification.id)
            return Response({'detail': 'Send Notification Successfully'}, status=200)
        else:
            return Response({'detail': 'Notification not send, something went wrong'}, status=422)
