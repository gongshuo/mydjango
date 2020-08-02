from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import ArticleColumn, ArticlePost, ArticleTag
from .forms import ArticleColumnForm, ArticlePostForm, ArticleTagForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# 引入分页功能用到的三个类
import json


@login_required(login_url='/account/login/')
@csrf_exempt
# 在视图函数前面添加装饰器的方式也是解决提交表单中遇到的CSRF 问题的一种方式。
def article_column(request):
    """新增栏目"""
    if request.method == "GET":
        columns = ArticleColumn.objects.filter(user=request.user)
        column_form = ArticleColumnForm()
        return render(request, "article/column/article_column.html", {"columns": columns, 'column_form': column_form})

    if request.method == "POST":
        column_name = request.POST['column']
        columns = ArticleColumn.objects.filter(user_id=request.user.id, column=column_name)
        if columns:
            # 如果已经存在columns
            return HttpResponse('2')
        else:
            ArticleColumn.objects.create(user=request.user, column=column_name)
            return HttpResponse("1")


@login_required(login_url='/account/login')
@require_POST
# 使用这个装饰器的目的就是保证此视图函数只接收通过POST方式提交的数据。
@csrf_exempt
def rename_article_column(request):
    """重命名column"""
    column_name = request.POST["column_name"]
    column_id = request.POST['column_id']
    try:
        line = ArticleColumn.objects.get(id=column_id)
        line.column = column_name
        line.save()
        return HttpResponse("1")
    except:
        return HttpResponse("0")


@login_required(login_url='/account/login')
@require_POST
@csrf_exempt
def del_article_column(request):
    """删除column"""
    column_id = request.POST["column_id"]
    try:
        line = ArticleColumn.objects.get(id=column_id)
        line.delete()
        return HttpResponse("1")
    except:
        return HttpResponse("2")


@login_required(login_url='/account/login')
@csrf_exempt
def article_post(request):
    """发布文章"""
    if request.method == "POST":  # 带数据
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            cd = article_post_form.cleaned_data
            try:
                new_article = article_post_form.save(commit=False)
                new_article.author = request.user
                new_article.column = request.user.article_column.get(id=request.POST['column_id'])
                new_article.save()
                # slug在重写的save中赋值，其他取默认值
                tags = request.POST['tags']
                if tags:
                    for atag in json.loads(tags):  # 将json解析
                        tag = request.user.tag.get(tag=atag)
                        new_article.article_tag.add(tag)
                        # 关联表增加数据，article_tag表无数据增加
                return HttpResponse("1")
            except:
                return HttpResponse("2")
        else:
            return HttpResponse("3")
    else:
        article_post_form = ArticlePostForm()
        article_columns = request.user.article_column.all()
        # article_column中有user_id
        article_tags = request.user.tag.all()
        return render(request, "article/column/article_post.html",
                      {"article_post_form": article_post_form, "article_columns": article_columns,
                       "article_tags": article_tags})


@login_required(login_url='/account/login')
def article_list(request):
    """查看文章列表"""
    #   http://127.0.0.1:8000/article/article-list/
    articles_list = ArticlePost.objects.filter(author=request.user)
    paginator = Paginator(articles_list, 4)
    # 创建分页的实例对象，并且规定每页最多2个
    page = request.GET.get('page')  # 如果为空，也不报错
    # 语句②获得当前浏览器GET请求的参数page的值
    try:
        current_page = paginator.page(page)
        # page()是Paginator对象的一个方法，其作用在于得到指定页面内容，其参数必须是大于或等于1的整数。
        articles = current_page.object_list
        # object_list是Page对象的属性，能够得到该页所有的对象列表。类似的属性还有Page.number（返回页码）等
    except PageNotAnInteger:
        # 请求的页码数值不是整数（PageNotAnInteger） 比如None
        current_page = paginator.page(1)
        articles = current_page.object_list
    except EmptyPage:
        # 请求的页码数值为空或者在URL参数中没有page
        current_page = paginator.page(paginator.num_pages)  # 最后一页
        # paginator.num_pages 返回的是页数，num_pages是Paginator对象的一个属性。
        articles = current_page.object_list
    return render(request, "article/column/article_list.html", {"articles": articles, "page": current_page})


@login_required(login_url='/account/login')
def article_detail(request, id, slug):
    """文章明细",通过models获取的地址跳转"""
    article = get_object_or_404(ArticlePost, id=id, slug=slug)
    return render(request, "article/column/article_detail.html", {"article": article})


@login_required(login_url='/account/login')
@require_POST
@csrf_exempt
def del_article(request):
    """删除文章"""
    article_id = request.POST['article_id']
    try:
        article = ArticlePost.objects.get(id=article_id)
        article.delete()
        return HttpResponse("1")
    except:
        return HttpResponse("2")


@login_required(login_url='/account/login')
@csrf_exempt
def redit_article(request, article_id):
    """编辑文章"""
    if request.method == "GET":
        article_columns = request.user.article_column.all()  # 获取用户的所有column
        article = ArticlePost.objects.get(id=article_id)

        this_article_form = ArticlePostForm(initial={"title": article.title})
        this_article_column = article.column
        return render(request, "article/column/redit_article.html",
                      {"article": article, "article_columns": article_columns,
                       "this_article_column": this_article_column, "this_article_form": this_article_form})
    else:
        redit_article = ArticlePost.objects.get(id=article_id)  # 获取的是一个models对象
        try:
            redit_article.column = request.user.article_column.get(id=request.POST['column_id'])
            redit_article.title = request.POST['title']
            redit_article.body = request.POST['body']
            redit_article.save()
            return HttpResponse("1")
        except:
            return HttpResponse("2")


@login_required(login_url='/account/login')
@csrf_exempt
def article_tag(request):
    """添加标签"""
    if request.method == "GET":
        article_tags = ArticleTag.objects.filter(author=request.user)
        article_tag_form = ArticleTagForm()
        return render(request, "article/tag/tag_list.html",
                      {"article_tags": article_tags, "article_tag_form": article_tag_form})

    if request.method == "POST":
        tag_post_form = ArticleTagForm(data=request.POST)
        if tag_post_form.is_valid():
            try:
                new_tag = tag_post_form.save(commit=False)

                if request.user.tag.filter(tag=request.POST['tag']).count():  # 注意，少了objects
                    return HttpResponse("用户【{}】已经有tag：{}".format(request.user, request.POST['tag']))

                new_tag.author = request.user
                new_tag.save()
                return HttpResponse("1")
            except:
                return HttpResponse("the data cannot be save.")
        else:
            return HttpResponse("sorry, the form is not valid.")


@login_required(login_url='/account/login')
@require_POST
@csrf_exempt
def del_article_tag(request):
    """删除标签"""
    tag_id = request.POST['tag_id']
    try:
        tag = ArticleTag.objects.get(id=tag_id)
        tag.delete()
        return HttpResponse("1")
    except:
        return HttpResponse("2")