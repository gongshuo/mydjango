from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.base import TemplateResponseMixin
# TemplateResponseMixin类，它提供了一种模板渲染的机制，在子类中，可以指定模板文件和渲染数据。
from django.views import View
from .models import Course, Lesson
from .forms import CreateCourseForm, CreateLessonForm

from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.http import HttpResponse

from braces.views import LoginRequiredMixin
import json


class CourseListView(ListView):
    model = Course
    context_object_name = "courses"
    template_name = 'course/course_list.html'


class AboutView(TemplateView):
    template_name = "course/about.html"


class UserMixin:
    def get_queryset(self):
        qs = super(UserMixin, self).get_queryset()
        return qs.filter(user=self.request.user)


# class UserCourseMixin(UserMixin):
#     model = Course

class UserCourseMixin(UserMixin, LoginRequiredMixin):
    model = Course
    login_url = "/account/login/"


class ManageCourseListView(UserCourseMixin, ListView):
    context_object_name = "courses"
    template_name = 'course/manage/manage_course_list.html'


class CreateCourseView(UserCourseMixin, CreateView):
    # 当用户以GET方式请求时，即在页面中显示表单，CreateView就是完成这个作用的类，只要继承它，就不需要写get()方法了。
    fields = ['title', 'overview']
    template_name = 'course/manage/create_course.html'

    def post(self, request, *args, **kargs):
        # 门处理以POST方式提交的表单内容，处理方法与以往的方法一样。
        form = CreateCourseForm(data=request.POST)
        if form.is_valid():
            new_course = form.save(commit=False)
            new_course.user = self.request.user
            new_course.save()
            return redirect("course:manage_course")
            # 当表单内容被保存后，将页面转向指定位置。
        return self.render_to_response({"form": form})
        # 在表单数据检测不通过时，让用户重新填写，注意这里没有使用render()


class DeleteCourseView(UserCourseMixin, DeleteView):
    # template_name = 'course/manage/delete_course_confirm.html'
    success_url = reverse_lazy("course:manage_course")

    def dispatch(self, *args, **kwargs):
        resp = super(DeleteCourseView, self).dispatch(*args, **kwargs)
        if self.request.is_ajax():
            response_data = {"result": "ok"}
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return resp


class CreateLessonView(LoginRequiredMixin, View):
    model = Lesson
    login_url = "/account/login/"

    def get(self, request, *args, **kwargs):
        form = CreateLessonForm(user=self.request.user)
        return render(request, "course/manage/create_lesson.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = CreateLessonForm(self.request.user, request.POST, request.FILES)
        # 重写了初始化函数__init__()，并且增加了一个参数user，所以在实例化时需要传入user值。
        # 因为提交的表单中有上传的文件，所以必须传入request.FILES。
        if form.is_valid():
            new_lesson = form.save(commit=False)
            new_lesson.user = self.request.user
            new_lesson.save()
            return redirect("course:manage_course")


class ListLessonsView(LoginRequiredMixin, TemplateResponseMixin, View):
    login_url = "/account/login/"
    template_name = 'course/manage/list_lessons.html'

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        return self.render_to_response({'course': course})


class DetailLessonView(LoginRequiredMixin, TemplateResponseMixin, View):
    login_url = "/account/login/"
    template_name = "course/manage/detail_lesson.html"

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        return self.render_to_response({"lesson": lesson})
        # render_to_response()就是TemplateResponseMixin类的方法。


class StudentListLessonView(ListLessonsView):
    template_name = "course/slist_lessons.html"

    def post(self, request, *args, **kwargs):
        course = Course.objects.get(id=kwargs['course_id'])
        course.student.add(self.request.user)
        return HttpResponse("ok")