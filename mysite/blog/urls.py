from django.urls import path, re_path
from . import views


app_name = 'blog'
urlpatterns = [
    path('', views.blog_title, name="blog_title"),
    re_path(r'(?P<article_id>\d)/$', views.blog_article, name='blog_article'),
    # path('<int;article_id>/',views.blog_article, name='blog_article'),
]
