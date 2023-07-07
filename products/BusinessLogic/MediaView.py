
import boto3
from datetime import datetime
from django.conf import settings
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from products.models import Media


class MediaView(APIView):
    swagger_schema = None

    def post(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            images = []
            if len(request.FILES) == 1:
                if 'file' in request.FILES:
                    images.append(request.FILES.get('file'))
                else:
                    images.append(request.FILES.get('file0'))

                try:
                    request.FILES.get('file')
                except Exception as e:
                    print(e)
            else:
                index = 0
                for i in range(0, len(request.FILES)):
                    images.append(request.FILES.get('file' + str(index)))
                    index = index + 1
            data = []

            for image in images:
                file_name = image.name
                split_name = file_name.rsplit('.', 1)
                file_extension = split_name[-1]
                file_name = remove_specialcharacters(split_name[0].lower()).replace(' ', '-') + '.' + file_extension
                try:
                    media_object = Media.objects.get(file_name=file_name)
                    if media_object:
                        now = datetime.now()
                        file_name = str(now.strftime('%d%m%y%H%M%S')).replace(' ', '-') + file_name
                except Exception as e:
                    print(e)

                media = Media()
                object_name = image
                s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                bucket_path = settings.AWS_BUCKET_PATH
                file_path = "products/product_images/" + file_name
                s3_params = {'StorageClass': "STANDARD_IA", 'ACL': 'public-read'}
                if file_extension == 'svg':
                    s3_params['ContentType'] = 'image/svg+xml'

                s3.upload_fileobj(object_name.file, bucket_path, file_path,
                                  ExtraArgs=s3_params)

                file_url = settings.AWS_BASE_URL + "/" + file_path
                media.file_path = file_path
                media.cdn_link = file_url
                media.file_name = file_name
                media.deleted = False
                media.deleted_at = None
                media.save()
                data.append({
                    "id": media.id,
                    "file_path": media.file_path,
                    "cdn_link": media.cdn_link,
                    "file_name": media.file_name
                })
            return Response(data, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    def delete(self, request):
        access = AccessApi(self.request.user, "products")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
            if obj_id is not None:
                Media.objects.filter(id=obj_id).update(deleted=True, deleted_at=datetime.now())
            else:
                return Response({"detail": "Media ID not found in request"}, status=404)

            # Post Entry in Logs
            action_performed = request.user.username + " deleted customer"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": "Deleted Media Successfully!"}, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)