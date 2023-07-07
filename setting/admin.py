from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(StoreInformation)
class StoreInformationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StoreInformation._meta.fields]