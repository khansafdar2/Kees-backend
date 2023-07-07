from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Customer._meta.fields]

@admin.register(Notes)
class NotesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Notes._meta.fields]

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Address._meta.fields]

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Tags._meta.fields]