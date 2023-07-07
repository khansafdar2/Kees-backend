
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import User
from authentication.Serializer.ChangePasswordSerializer import ChangePasswordSerializer
from authentication.BusinessLogic.ActivityStream import SystemLogs
from drf_yasg.utils import swagger_auto_schema


# Password Change API
class ChangePassword(APIView):

    @swagger_auto_schema(responses={200: ChangePasswordSerializer}, request_body=ChangePasswordSerializer)
    def put(self, request):
        request_data = request.data
        serializer = ChangePasswordSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(id=request.user.id).first()
        user.set_password(serializer.validated_data['password'])
        user.changePassword = False
        user.save()

        # Post Entry in Logs
        action_performed = request.user.username + " changed password of " + user.username
        SystemLogs.post_logs(self, request, request.user, action_performed)

        content = {"detail": "Password Changed"}
        return Response(content)
