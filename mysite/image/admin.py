from django.contrib import admin

# Register your models here.
from .models import Image


class ImageAdmin(admin.ModelAdmin):
    list_display = ("user", "title", 'url', 'slug')


admin.site.register(Image,ImageAdmin)