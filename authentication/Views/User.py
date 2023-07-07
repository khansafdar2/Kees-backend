
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.Serializer.UserSerializer import \
    UserListSerializer, \
    UserDeleteSerializer, \
    AddUserSerializer, \
    UpdateUserSerializer
from authentication.Serializer.RolePermissionSerializer import RolePermissionSerializer
from authentication.models import User, RolePermission
from authentication.Views.SignIn import dummy_permission
from authentication.BusinessLogic.ActivityStream import SystemLogs
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


# User CRUD
class UserView(APIView):

    @swagger_auto_schema(responses={200: UserListSerializer(many=True)})
    def get(self, request):
        try:
            access = AccessApi(self.request.user, "configuration")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            query_set = User.objects.filter(is_vendor=False, deleted=False)
            if not query_set:
                data = {}
                return Response(data, status=200)
            serializer = UserListSerializer(query_set, many=True)

            # Post Entry in Logs
            action_performed = request.user.username + " fetch all users"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({'users': serializer.data}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    @swagger_auto_schema(responses={200: AddUserSerializer}, request_body=AddUserSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data

        user = AddUserSerializer(data=request_data)
        if user.is_valid(raise_exception=True):
            user.save()

            # Post Entry in Logs
            action_performed = request.user.username + " created User"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(user.data, status=200)
        else:
            return Response(user.errors, status=422)

    @swagger_auto_schema(responses={200: UpdateUserSerializer}, request_body=UpdateUserSerializer)
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

        try:
            permissions = request_data['permissions']
        except Exception as e:
            print(e)
            permissions = False

        if permissions:
            if obj_id == self.request.user.id:
                raise exceptions.ParseError("User can not update its permissions")

        user = User.objects.filter(id=obj_id, is_vendor=False, deleted=False).first()
        serializer = UpdateUserSerializer(user, data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update user account of " + user.username
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class UserDetailView(APIView):
    @swagger_auto_schema(responses={200: UserListSerializer})
    def get(self, request, pk):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            instance = User.objects.get(pk=pk, is_vendor=False)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = UserListSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single user"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data)

    @swagger_auto_schema(responses={200: UserDeleteSerializer}, request_body=UserDeleteSerializer)
    def delete(self, request, pk):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        obj_id = pk
        if obj_id is not None:
            try:
                RolePermission.objects.filter(user_id=obj_id).update(deleted=True, deleted_at=datetime.now())
                User.objects.filter(id=obj_id, is_vendor=False).update(is_active=False, deleted=True, deleted_at=datetime.now())
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "User ID not found in request"}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + " deleted User"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted User Successfully!"}, status=200)


# User Role Permission
class UserRolePermission(APIView):
    @swagger_auto_schema(responses={200: RolePermissionSerializer})
    def get(self, request):
        access = AccessApi(self.request.user, "configuration")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        api_key = request.META.get('HTTP_AUTHORIZATION')
        try:
            user = User.objects.filter(token=api_key).first()
            if user.role_permission_id is None:
                role_obj = dummy_permission()
            else:
                try:
                    role_permission = RolePermission.objects.filter(id=user.role_permission_id).first()
                    serializer = RolePermissionSerializer(role_permission)
                    role_obj = serializer.data
                except Exception as e:
                    print(e)
                    role_obj = dummy_permission()
        except Exception as e:
            print(e)
            role_obj = dummy_permission()

        return Response({"role_permission": role_obj}, status=200)


class CheckUserNameEmail(APIView):
    def get(self, request):
        username = request.GET.get('username', None)
        email = request.GET.get('email', None)

        if username is not None:
            user = User.objects.filter(username=username).first()
            if user:
                return Response({'detail': 'username already exist'}, status=400)
            return Response({'detail': 'Username is available'}, status=200)

        if email is not None:
            user = User.objects.filter(email=email).first()
            if user:
                if not user.deleted:
                    return Response({'detail': 'email already exist'}, status=400)
                else:
                    return Response({'username': user.username}, status=200)
            return Response({'email': 'Email is available'}, status=200)
