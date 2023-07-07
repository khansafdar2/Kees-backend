from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Page._meta.fields]


@admin.register(PriceRangeFilter)
class PageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PriceRangeFilter._meta.fields]


@admin.register(StoreFilter)
class PriceRangeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StoreFilter._meta.fields]


@admin.register(SEO)
class SEOAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SEO._meta.fields]


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Template._meta.fields]


@admin.register(Preferences)
class PreferencesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Preferences._meta.fields]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MenuItem._meta.fields]