
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters
import boto3
from django.conf import settings


def media_upload(image):
    file_name = image.name
    split_name = file_name.rsplit('.', 1)
    file_extension = split_name[-1]
    file_name = remove_specialcharacters(split_name[0].lower()).replace(' ', '-') + '.' + file_extension

    object_name = image
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket_path = settings.AWS_BUCKET_PATH
    file_path = "products/product_images/" + file_name
    s3.upload_fileobj(object_name.file, bucket_path, file_path,
                      ExtraArgs={'StorageClass': "STANDARD_IA", 'ACL': 'public-read'})

    file_url = settings.AWS_BASE_URL + "/" + file_path
    return file_url
