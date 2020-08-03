from django.utils.safestring import mark_safe
# django.utils.safestring的作用就是将字符串编程为“safe strings”

import markdown

from django import template
# 引入了django.template 库，它里面包含着诸多与模板有关的类和方法等

register = template.Library()

from article.models import ArticlePost


@register.simple_tag
# 通过装饰器，表明其下面的代码是自定义的simple_tag类型的标签。
def total_articles():
    # 文章总数
    return ArticlePost.objects.count()


@register.simple_tag
def author_total_articles(user):
    # 获取作者所有文章
    return user.article.count()


@register.inclusion_tag('article/list/latest_articles.html')
# 使用装饰器来声明自定义的标签类型，只不过这次增加了参数，用('article/list/latest_articles.html')确定所渲染的模板文件。
def latest_articles(n=5):
    # 最新文章
    latest_articles = ArticlePost.objects.order_by("-created")[:n]
    return {"latest_articles": latest_articles}
    # 返回语句④样式的字典类型的数据，此数据被应用到语句①中所指定的模板文件中。


from django.db.models import Count 
@register.simple_tag
def most_commented_articles(n=3):
    # 最多评论文章
    # 以参数的形式说明显示评论最多的文章数量，这里默认显示评论数量最多的前3篇。
    return ArticlePost.objects.annotate(total_comments=Count('comments')).order_by("-total_comments")[:n]
    # annotate()函数是要给查询到的文章对象进行标注。用什么标注呢？就是里面的参数Count("comments")。


@register.filter(name='markdown')
# 语句①的作用是重命名语句②中的选择器函数，即将名字由markdown_filter 修改为markdown。
# 将Markdown编码转换为HTML代码的选择器函数
def markdown_filter(text):
    return mark_safe(markdown.markdown(text))