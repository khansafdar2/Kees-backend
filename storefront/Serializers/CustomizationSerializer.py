
from cms.models import Newsletter, Customization, Navigation
from products.models import Media, Brand, MainCategory
from storefront.BussinessLogic.HomePageProductSlider import productslider
from storefront.Serializers.StorefrontCategorySerializer import CategoriesListSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.response import Response


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ('email',)
        validators = [
            UniqueTogetherValidator(
                queryset=Newsletter.objects.filter(deleted=False),
                fields=['email']
            )
        ]

    def create(self, validate_data):
        instance = Newsletter.objects.create(**validate_data)
        return instance


class HomePageSerializer(serializers.ModelSerializer):
    homepage = serializers.SerializerMethodField('get_homepage')

    class Meta:
        model = Customization
        fields = ('homepage',)

    def get_homepage(self, obj):
        home_page = obj.homepage_json['sections']
        for count, section in enumerate(obj.homepage_json['sections']):
            if section['type'] == 'categories_carousel':
                for category_counter, category in enumerate(section['categories']):
                    handle = category['handle']
                    products_list = productslider(handle)
                    home_page[count]['categories'][category_counter]['products'] = products_list

            brand_list = []
            if section['type'] == 'brands_slider':
                brands = section['brands']
                for brand in brands:
                    queryset = Brand.objects.filter(handle=brand['handle'], deleted=False).first()
                    if queryset:
                        if brand['logo']:
                            brand_image = brand['logo']
                        else:
                            brand_image = Media.objects.filter(brand=queryset, deleted=False).exclude(
                                file_name="brand_banner").first()
                            if brand_image is not None:
                                brand_image = brand_image.cdn_link
                            else:
                                brand_image = None

                        brand_data = {
                            'name': queryset.name,
                            'handle': queryset.handle,
                            'logo': brand_image
                        }
                        brand_list.append(brand_data)

                home_page[count]['brands'] = brand_list

            if section['type'] == 'products_carousel':
                handle = section['category_handle']
                products_list = productslider(handle)
                home_page[count]['products'] = products_list

            if section['type'] == 'categories_tabs':
                for category_counter, category in enumerate(section['categories']):
                    handle = category['handle']
                    products_list = productslider(handle)
                    home_page[count]['categories'][category_counter]['products'] = products_list

        return home_page


class HeaderSerializer(serializers.ModelSerializer):
    header = serializers.SerializerMethodField('get_header')

    class Meta:
        model = Customization
        fields = ('header',)

    def get_header(self, obj):
        header = obj.header

        # navigation attachments
        navigation_id = header["navigation_bar"]["navigation"]
        navigation = Navigation.objects.filter(id=navigation_id, deleted=False).first()
        header["navigation_bar"]["navigation_title"] = navigation.title
        header["navigation_bar"]["navigation"] = navigation.navigation_json

        # category
        query_set = MainCategory.objects.filter(is_active=True, deleted=False).order_by('position')
        if not query_set:
            data = {}
            return Response(data, status=200)
        serializer = CategoriesListSerializer(query_set, many=True)
        header["navigation_bar"]["category_structure"] = serializer.data
        return header


class FooterSerializer(serializers.ModelSerializer):
    footer = serializers.SerializerMethodField('get_footer')

    class Meta:
        model = Customization
        fields = ['footer']

    def get_footer(self, obj):
        footer = obj.footer

        # navigation attachments
        navigations = footer["navigations"]
        for nav in navigations:
            navigation = Navigation.objects.filter(id=nav["id"], deleted=False).first()
            if navigation:
                nav["title"] = navigation.title
                nav["menu"] = navigation.navigation_json

        return footer
