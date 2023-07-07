
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.Serializer.TransferOwnershipSerializer import TransferOwnershipSerializer
from authentication.models import User, RolePermission
from authentication.BusinessLogic.ActivityStream import SystemLogs
from drf_yasg.utils import swagger_auto_schema


# User CRUD
class TransferOwner(APIView):

    @swagger_auto_schema(responses={200: TransferOwnershipSerializer}, request_body=TransferOwnershipSerializer)
    def post(self, request):
        try:
            request_data = request.data
            if request.user.id == request_data['id']:
                return Response({"detail": "Cannot assign yourself as Owner!"}, status=422)
            if request.user.is_owner:
                User.objects.filter(id=request_data['id']).update(is_superuser=True, is_owner=True, is_admin=True)
                request.user.is_superuser = False
                request.user.is_owner = False
                request.user.is_admin = True
                request.user.save()

                try:
                    RolePermission.objects.get(user=request.user)
                except Exception as e:
                    print(e)
                    permissions_data = {
                        "dashboard": True,
                        "theme": True,
                        "products": True,
                        "orders": True,
                        "customer": True,
                        "discounts": True,
                        "configuration": True,
                        "vendor": True
                    }
                    RolePermission.objects.create(user=request.user, **permissions_data)

                # Post Entry in Logs
                action_performed = request.user.username + " transfer Ownership"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response({"detail": "Ownership transferred successfully!"}, status=200)
            else:
                return Response({"detail": "Only owner has the right to transfer ownership!"}, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=422)
