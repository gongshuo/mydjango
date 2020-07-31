from django.shortcuts import render,get_object_or_404

from . import  models

# Create your views here.


def blog_title(request):
    blogs = models.BlogArticles.objects.all()
    return  render(request, 'blog/title.html', {'blogs':blogs})
