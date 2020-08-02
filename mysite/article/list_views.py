from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from .models import ArticleColumn, ArticlePost, Comment
from .forms import CommentForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required 
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_POST
from django.db.models import Count

import redis  # https://github.com/tporadowski/redis/releases
# r = redis.StrictRedis(host='localhost', port=6379, db=0)
from django.conf import settings
# 引入本项目setting.py中的变量，从而能够在下一句的数据库连接中使用。
r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


def article_titles(request, username=None):
    # 这种方式兼顾两种可能，一种是直接请求所有文章标题，另外一种是请求某个用户（作者）的文章标题。
    if username:
        user = User.objects.get(username=username)
        articles_title = ArticlePost.objects.filter(author=user)
        try:
            userinfo = user.userinfo
        except:
            userinfo = None
    else:
        articles_title = ArticlePost.objects.all()
    #articles_title = ArticlePost.objects.all() 
    paginator = Paginator(articles_title, 2) 
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        articles = current_page.object_list 
    except PageNotAnInteger:
        current_page = paginator.page(1)
        articles = current_page.object_list 
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages) 
        articles = current_page.object_list
    
    if username:
        return render(request, "article/list/author_articles.html", {"articles":articles, "page":current_page, "userinfo":userinfo, "user":user})
    return render(request, "article/list/article_titles.html", {"articles":articles, "page": current_page})


def article_detail(request, id, slug):
    article = get_object_or_404(ArticlePost, id=id, slug=slug)
    # 对访问文章的次数进行记录
    # incr函数的作用就是让当前的键值递增，并返回递增后的值。
    total_views = r.incr("article:{}:views".format(article.id))
    r.zincrby('article_ranking', 1, article.id)
    # 根据amount所设定的步长值增加有序集合（name）中的value的数值。
    # 在语句①中实现了aticle_ranking中的article.id 以步长1 自增，
    # 即文章被访问一次，article_ranking就将该文章id的值增加1。
    article_ranking = r.zrange("article_ranking", 0, -1, desc=True)[:10]
    # 得到article_ranking中排序前10 名的对象。
    article_ranking_ids = [int(id) for id in article_ranking]
    most_viewed = list(ArticlePost.objects.filter(id__in=article_ranking_ids))
    # 查询出id在article_ranking_ids中的所有文章对象
    most_viewed.sort(key=lambda x: article_ranking_ids.index(x.id))
    
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST) 
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False) 
            new_comment.article = article 
            new_comment.save()
    else:
        comment_form = CommentForm()
    article_tags_ids = article.article_tag.values_list("id", flat=True)
    # 如果不声明flat=True，列表是由元组组成的
    similar_articles = ArticlePost.objects.filter(article_tag__in=article_tags_ids).exclude(id=article.id)
    similar_articles = similar_articles.annotate(same_tags=Count("article_tag")).order_by('-same_tags', '-created')[:4]
    return render(request, "article/list/article_content.html", {"article":article,
                                                                 "total_views":total_views,
                                                                 "most_viewed": most_viewed,
                                                                 "comment_form":comment_form,
                                                                 "similar_articles":similar_articles})
    #return render(request, "article/list/article_content.html", {"article":article})

@csrf_exempt
@require_POST 
@login_required(login_url='/account/login/') 
def like_article(request):
    article_id = request.POST.get("id")
    action = request.POST.get("action")
    if article_id and action:
        try:
            article = ArticlePost.objects.get(id=article_id) 
            if action=="like":
                article.users_like.add(request.user)
                return HttpResponse("1") 
            else:
                article.users_like.remove(request.user)
                return HttpResponse("2") 
        except:
            return HttpResponse("no")