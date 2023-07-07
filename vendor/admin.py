from django.contrib import admin
from .models import *
from django import forms
# Register your models here.
@admin.register(Vendor)
class UserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Vendor._meta.fields]