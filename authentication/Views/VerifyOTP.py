
import datetime
from rest_framework.response import Response
from rest_framework.views import APIView


class VerifyOTP(APIView):

    def get(self, request):
        otp = request.GET.get('otp')
        user = request.user
        if user is not None:
            if user.email_2fa or user.phone_2fa:
                if otp == user.phone_otp or otp == user.email_otp:
                    now = datetime.datetime.now()
                    expiry = user.otp_expiry
                    difference = (now - expiry).total_seconds()
                    difference = int(difference)
                    if difference < 61:
                        user.otp_expiry = None
                        user.save()
                    else:
                        return Response({"detail": "OTP expire"}, status=401)
                else:
                    return Response({"detail": "Invalid OTP"}, status=401)

            if user.phone_2fa or user.email_2fa:
                return Response({"detail": "success"}, status=200, content_type='application/json')
            return Response({"detail": "2FA not found"}, status=401)
        else:
            return Response({"detail": "User not found"}, status=401)
