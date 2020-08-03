from django.urls import path
from . import views

app_name = 'image'

urlpatterns = [
    path('list-images/', views.list_images, name="list_images"),  # 图片管理
    path('upload-image/', views.upload_image, name='upload_image'),  # 上传图片
    path('del-image/', views.del_image, name='del_image'),
    path('images/', views.falls_images, name="falls_images"),  # 瀑布图片
    ]
