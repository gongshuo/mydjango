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


def testview(request):
    return HttpResponse('<h1>Hello,learn course together</h1>')


class AboutView(TemplateView):
    template_name = "course/about.html"


class CourseListView(ListView):
    model = Course  # 没有使用Course.objects.all()，而是用语句④的方式非常简洁地表达了。
    # queryset = Course.objects.filter(user=User.objects.filter(username='niulaoshi').first())        # 和get_queryset等效
    context_object_name = "courses"  # 声明了传入模板中的变量名称
    template_name = 'course/course_list.html'
    #
    #
    # def get_queryset(self):
    #     qs = super(CourseListView, self).get_queryset()             # 读取数据库并返回结果（QuerySet）
    #     return qs.filter(user=User.objects.filter(username="root").first())    # ⑧


class UserMixin:
    def get_queryset(self):
        qs = super(UserMixin, self).get_queryset()
        return qs.filter(user=self.request.user)


# class UserCourseMixin(UserMixin):
# model = Course

class UserCourseMixin(UserMixin, LoginRequiredMixin):
    model = Course
    login_url = "/account/login/"


class ManageCourseListView(UserCourseMixin, ListView):
    """用于用户登录后，进入“后台管理”，对课程进行“增删改查”等操作。"""
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
        # 重写了DeleteView类中的dispatch()方法 ，原本在DeleteView类中执行dispatch()方法后
        resp = super(DeleteCourseView, self).dispatch(*args, **kwargs)
        if self.request.is_ajax():
            # 通过语句⑤进行判断，如果是Ajax方法提交过来的数据，就直接反馈HttpResponse对象给前端，
            # 前端的JavaScript函数得到反馈结果，这样就完成了删除和页面的刷新。
            response_data = {"result": "ok"}
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return resp


def rename_course_name(request):
    if request.method == 'POST':
        new_course_id = request.POST['course_id']
        new_course_title = request.POST['new_title']
        course = Course.objects.filter(title=new_course_title)
        if course:
            # 如果已经存在columns
            return HttpResponse('2')
        else:
            course = Course.objects.filter(id=new_course_id).first()
            course.title = new_course_title
            course.save()
            return HttpResponse("1")

    else:
        return HttpResponse('<h1>你使用的是get方法</h1>')


class CreateLessonView(LoginRequiredMixin, View):
    """创建课程"""
    # 在View类中没有默认的get()和post()方法
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
    """课程列表"""
    login_url = "/account/login/"
    template_name = 'course/manage/list_lessons.html'
    # template_name = 'course/slist_lessons.html'

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