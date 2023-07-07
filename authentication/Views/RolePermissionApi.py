
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.Serializer.RolePermissionSerializer import RolePermissionSerializer, RolePermissionListSerializer
from authentication.models import RolePermission
from authentication.BusinessLogic.ActivityStream import SystemLogs
from drf_yasg.utils import swagger_auto_schema


# Role Permission CRUD
class RolePermissionView(APIView):

    @swagger_auto_schema(responses={200: RolePermissionListSerializer(many=True)})
    def get(self, request):
        # Post Entry in Logs
        action_performed = request.user.username + "fetch all role and permissions"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        role_permissions = RolePermission.objects.all().order_by('-id').values()
        serializer = RolePermissionListSerializer(role_permissions, many=True)
        return Response({'role_permissions': serializer.data}, status=200)

    @swagger_auto_schema(responses={200: RolePermissionSerializer}, request_body=RolePermissionSerializer)
    def post(self, request):
        request_data = request.data
        role_permission = RolePermissionSerializer(data=request_data)
        if role_permission.is_valid(raise_exception=True):
            role_permission.save()

            # Post Entry in Logs
            action_performed = request.user.username + " create role permission " + role_permission.name
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": "Role created"}, status=201)
        else:
            return Response(role_permission.errors, status=422)

    @swagger_auto_schema(responses={200: RolePermissionSerializer}, request_body=RolePermissionSerializer)
    def put(self, request):
        obj_id = request.data.get("id", None)
        request_data = request.data
        if obj_id is None:
            serializer = RolePermissionSerializer(data=request_data)
        else:
            role_permission = RolePermission.objects.filter(id=obj_id).first()
            serializer = RolePermissionSerializer(role_permission, data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update role permission " + serializer.name
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


# Role Permission List View
class RolePermissionList(APIView):

    @swagger_auto_schema(responses={200: RolePermissionSerializer(many=True)})
    def get(self, request):
        role_permissions = RolePermission.objects.all().order_by('-id').values()
        serializer = RolePermissionSerializer(role_permissions, many=True)
        return Response({'role_permissions': serializer.data}, status=200)


# Role Permission Data from User Drop Down
class RolePermissionItem(APIView):

    @swagger_auto_schema(responses={200: RolePermissionSerializer})
    def get(self, request):
        role_permission = RolePermission.objects.filter(id=request.GET.get('id')).first()
        serializer = RolePermissionSerializer(role_permission)
        return Response({'role_permissions': serializer.data}, status=200)
