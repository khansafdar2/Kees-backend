from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from cms.models import MenuItem
from cms.Serializers.MenuSerializer import MenuSerializer
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class MenuView(APIView):

    @swagger_auto_schema(responses={200: MenuSerializer(many=True)})
    def get(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        query_set = MenuItem.objects.filter(deleted=False)
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = MenuSerializer(query_set, many=True)
        data = []
        not_found = []
        for item in serializer.data:
            if item['parent'] is None:
                item['child_items'] = []
                data.append(item)
        for item in serializer.data:
            if item['parent']:
                parent = next((a for a in serializer.data if item['parent'] == a['id']), None)
                parent_obj = next((a for a in data if parent['id'] == a['id']), None)

                print()
                if parent_obj:
                    if parent_obj['parent'] is None:
                        item['child_items'] = []
                        parent_obj['child_items'].append(item)
                else:
                    if parent['parent'] is None:
                        parent['child_items'] = []
                        data.append(parent)
                        parent['child_items'].append(item)
                    else:
                        not_found.append(item)
        for item in not_found:
            index1 = 0
            for grand_parent in data:
                index2 = 0
                for parent in grand_parent['child_items']:
                    if parent['id'] == item['parent']:
                        data[index1]['child_items'][index2]['child_items'].append(item)
                    index2 += 1
                index1 += 1
        return Response(data, status=200)

    @swagger_auto_schema(responses={200: MenuSerializer}, request_body=MenuSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "customization")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
            menu = MenuSerializer(data=request_data)
            if menu.is_valid(raise_exception=True):
                menu.save()
                return Response(menu.data, status=200)
            else:
                return Response(menu.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)
    #
    # def put(self, request):
    #     try:
    #         obj_id = request.data["id"]
    #     except Exception as e:
    #         print(e)
    #         return Response({"detail": "ID not found in data!"}, status=400)
    #
    #     request_data = request.data
    #
    #     if obj_id is None:
    #         serializer = PageSerializer(data=request_data)
    #     else:
    #         page = Page.objects.filter(id=obj_id).first()
    #         serializer = PageSerializer(page, data=request_data)
    #
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=200)
    #     else:
    #         return Response(serializer.errors, status=422)
    #
    # def delete(self, request):
    #     obj_id = request.GET.get("id")
    #     if obj_id is not None:
    #         try:
    #             Page.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
    #         except Exception as e:
    #             return Response({"detail": e}, status=404)
    #     else:
    #         return Response({"detail": "Page ID not found in request"}, status=404)
    #
    #     return Response({"detail": "Deleted Page Successfully!"}, status=200)
    #

