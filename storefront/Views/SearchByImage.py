
import json
import requests
from rest_framework.response import Response
from rest_framework.views import APIView


class XimilarArtificialIntelligence(object):
    def object_parsing(self, ximilar_data):
        data = []

        if 'records' in ximilar_data:
            if len(ximilar_data['records']) == 1:
                records = ximilar_data['records'][0]
                if '_objects' in records:
                    objects_list = records['_objects']
                    for obj in objects_list:
                        if '_tags' in obj:
                            tags = obj['_tags']
                            combine_tags = [obj['Top Category'], obj['Category']]

                            ### Category ###
                            categories = []
                            if 'Category' in tags:
                                for tag in tags['Category']:
                                    categories.append(tag['name'])
                                    combine_tags.append(tag['name'])

                            ### Color ###
                            colors = []
                            if 'Color' in tags:
                                for tag in tags['Color']:
                                    colors.append(tag['name'])

                            ### Style ###
                            style = []
                            if 'Style' in tags:
                                for tag in tags['Style']:
                                    style.append(tag['name'])
                                    combine_tags.append(tag['name'])

                            ### Subcategory ###
                            sub_categories = []
                            if 'Subcategory' in tags:
                                for tag in tags['Subcategory']:
                                    sub_categories.append(tag['name'])
                                    combine_tags.append(tag['name'])

                            ### Gender ###
                            gender = []
                            if 'Gender' in tags:
                                for tag in tags['Gender']:
                                    gender.append(tag['name'])
                                    combine_tags.append(tag['name'])

                            ### Material ###
                            materials = []
                            if 'Material' in tags:
                                for tag in tags['Material']:
                                    materials.append(tag['name'])
                                    combine_tags.append(tag['name'])

                            ### Length ###
                            length = []
                            if 'Length' in tags:
                                for tag in tags['Length']:
                                    length.append(tag['name'])
                                    combine_tags.append(tag['name'])

                            ### Design ###
                            designs = []
                            if 'Design' in tags:
                                for tag in tags['Design']:
                                    designs.append(tag['name'])
                                    combine_tags.append(tag['name'])

                            ### Sleeves ###
                            sleeves = []
                            if 'Sleeves' in tags:
                                for tag in tags['Sleeves']:
                                    sleeves.append(tag['name'])
                                    combine_tags.append(tag['name'])

                            ### Cut ###
                            cut = []
                            if 'Cut' in tags:
                                for tag in tags['Cut']:
                                    cut.append(tag['name'])
                                    combine_tags.append(tag['name'])

                            tem_obj = {
                                'name': obj['name'],
                                'combine_tags': combine_tags,
                                'colors': colors,
                                'bound_box': obj['bound_box'],
                                'prob': obj['prob'],
                                'area': obj['area'],
                                'top_category': obj['Top Category'],
                                'category': obj['Category'],
                                'categories': categories,
                                'sub_categories': sub_categories,
                                'style': style,
                                'gender': gender,
                                'materials': materials,
                                'length': length,
                                'sleeves': sleeves,
                                'designs': designs,
                            }

                            data.append(tem_obj)
                        else:
                            combine_tags = [obj['Top Category'], obj['Category']]
                            tem_obj = {
                                'name': obj['name'],
                                'combine_tags': combine_tags,
                                'colors': [],
                                'bound_box': obj['bound_box'],
                                'prob': obj['prob'],
                                'area': obj['area'],
                                'top_category': obj['Top Category'],
                                'category': obj['Category'],
                                'sub_categories': [],
                                'style': [],
                                'gender': [],
                                'materials': [],
                                'length': [],
                                'sleeves': [],
                                'designs': []
                            }
                            data.append(tem_obj)
        return data


########## Search image by using image link ##########
class XimilarImageRekognitionLink(APIView):

    def post(self, request):
        try:
            # Build Rekognition Client to access the service
            image_link = request.data['image_link']

            endpoint_url = 'https://api.ximilar.com/tagging/fashion/v2/detect_tags'
            headers = {
                'Authorization': "Token cc6466fa64253d1d31820820c23554c96377e4e7",
                'Content-Type': 'application/json'
            }

            image_data = {
                'records': [{'_url': image_link}]
            }

            ####################################################################
            ####################################################################
            ##################### Addition Functionality #######################
            ####################################################################
            ####################################################################

            # img_bytes = requests.get(image_link).content

            # with open(_IMAGE_PATH_, "rb") as image_file:
            #     encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            # image_data = {
            #     'records': [{'_url': image_link}, {"_base64": encoded_string}]
            # }

            ####################################################################
            ####################################################################
            ##################### Addition Functionality #######################
            ####################################################################
            ####################################################################

            response = requests.post(endpoint_url, headers=headers, data=json.dumps(image_data))
            if response.status_code == 200:
                response_data = json.loads(response.text)
                parse_data = XimilarArtificialIntelligence.object_parsing(self, response_data)
            else:
                print('Error posting API: ' + str(response.status_code))
                print('Error posting API: ' + response.text)
                parse_data = {}

            data = {
                'tag_list': parse_data
            }

            return Response(data, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


########## Search image by uploading image ##########
class XimilarImageRekognitionUpload(APIView):

    def post(self, request):
        try:
            # Build Rekognition Client to access the service
            image = request.FILES.get('file')
            image_link = upload_to_s3(image, shop.myshopify_domain)

            endpoint_url = 'https://api.ximilar.com/tagging/fashion/v2/detect_tags'
            headers = {
                'Authorization': "Token cc6466fa64253d1d31820820c23554c96377e4e7",
                'Content-Type': 'application/json'
            }

            ####################################################################
            ####################################################################
            ##################### Addition Functionality #######################
            ####################################################################
            ####################################################################
            # img_bytes = image.file.read()

            # with open(_IMAGE_PATH_, "rb") as image_file:
            #     encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            # image_data = {
            #     'records': [{"_base64": img_bytes}]
            # }

            ####################################################################
            ####################################################################
            ##################### Addition Functionality #######################
            ####################################################################
            ####################################################################

            image_data = {
                'records': [{'_url': image_link}]
            }

            response = requests.post(endpoint_url, headers=headers, data=json.dumps(image_data))
            if response.status_code == 200:
                response_data = json.loads(response.text)
                parse_data = XimilarArtificialIntelligence.object_parsing(self, response_data)
            else:
                print('Error posting API: ' + str(response.status_code))
                print('Error posting API: ' + response.text)
                parse_data = {}

            data = {
                'tag_list': parse_data
            }

            return Response(data, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
