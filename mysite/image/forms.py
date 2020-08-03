from django import forms
from django.core.files.base import ContentFile
from slugify import slugify
from urllib import request
from .models import Image


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'url', 'description')

    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg', 'png']
        # 规定了图片的扩展名
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError("The given Url does not match valid image extension.")
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        image = super(ImageForm, self).save(commit=False)
        # commit=False意味着实例虽然被建立了，但并没有保存数据。

        image_url = self.cleaned_data['url']
        image_name = '{0}.{1}'.format(slugify(image.title), image_url.rsplit('.', 1)[1].lower())
        # 获取图片新名字，不含路径

        response = request.urlopen(image_url)
        # request不是视图函数中的参数request，而是Python标准库Urllib中的一部分，是一个很好的爬虫工具。
        # request.urlopen(image_url)的作用是以GET方式访问该图片地址

        image.image.save(image_name, ContentFile(response.read()), save=False)  # 有配置基础路径media
        # 使用response.read()就是要得到此数据。
        # ContentFile类是Django中File类的子类，它接收字符串为参数。
        if commit:
            image.save()

        return image