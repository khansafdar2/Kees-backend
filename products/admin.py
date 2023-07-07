from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Media._meta.fields]
