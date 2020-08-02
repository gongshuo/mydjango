from django.contrib import admin
from .models import Lesson, Course


# Register your models here.
class LessonAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "title", 'description')
    list_filter = ('title',)
    search_fields = ("user", "course", "title")
    raw_id_fields = ("course",)
    # date_hierarchy = "publish"
    ordering = ['user', 'course']


admin.site.register(Lesson, LessonAdmin)  # 将表BlogArticles注册到admin/


# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", 'overview')
#     list_filter = ('title',)
#     search_fields = ("user", "title")
#     raw_id_fields = ("title",)
#     # date_hierarchy = "publish"
#     ordering = ['title']


admin.site.register(Course)   # 将表BlogArticles注册到admin/