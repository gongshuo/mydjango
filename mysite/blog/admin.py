from django.contrib import admin
# Register your models here.
from .models import BlogArticles


class BlogArticlesAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publish")
    list_filter = ('title', "publish", "author")
    search_fields = ("title", "body")
    raw_id_fields = ("author",)
    date_hierarchy = "publish"
    ordering = ['-publish', 'author']


admin.site.register(BlogArticles, BlogArticlesAdmin)  # 将表BlogArticles注册到admin/
