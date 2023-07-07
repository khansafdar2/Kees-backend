
from datetime import datetime, timedelta
from crm.models import CustomerForgetPassword


def CheckExpiry(key, invite):
    utc_now = datetime.now()
    if invite.created_at < utc_now - timedelta(hours=1):
        CustomerForgetPassword.objects.filter(key=key).update(expired=True)
        return {
            "status": True,
            "message": "Forget Password link has been expired"
        }
    else:
        return {"status": False}