from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from slugify import slugify   # pip install awesome-slugify 支持中文
# from django.utils.text import slugify  # python 自带的


class ArticleColumn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_column', verbose_name='用户名')
    column = models.CharField(max_length=200, verbose_name='栏目')
    created = models.DateField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '文章表'

    def __str__(self):
        return self.column


class ArticleTag(models.Model):
    # 关于文章标签的数据模型类
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tag")
    # user获取articletag 使用request.user.tag.all()
    tag = models.CharField(max_length=500)

    def __str__(self):
        return self.tag


class ArticlePost(models.Model):
    """文章"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="article")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=500)
    column = models.ForeignKey(ArticleColumn, on_delete=models.CASCADE, related_name="article_column")

    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    # 点赞
    users_like = models.ManyToManyField(User, related_name="articles_like", blank=True)
    #
    article_tag = models.ManyToManyField(ArticleTag, related_name='article_tag', blank=True)

    class Meta:
        ordering = ("-updated",)
        index_together = (('id', 'slug'),)  # 对数据库中这两个字段建立索引

    def __str__(self):
        return self.title

    def save(self, *args, **kargs):
        self.slug = slugify(self.title)  # 重新save，self.slug赋值
        super(ArticlePost, self).save(*args, **kargs)

    def get_absolute_url(self):
        """给每篇文章添加明细路径"""
        return reverse("article:article_detail", args=[self.id, self.slug])
        # 通过reverse('article:article_detail')实现了'/article/article-list/'
        # 通过ArticlePost.get_absolute_url使每个文章都有链接

    def get_url_path(self):
        """给每篇文章添加路径"""
        return reverse("article:article_content", args=[self.id, self.slug])


class Comment(models.Model):
    article = models.ForeignKey(ArticlePost, on_delete=models.CASCADE, related_name="comments")
    commentator = models.CharField(max_length=90)  # 评论人
    body = models.TextField()  # 评论内容
    created = models.DateTimeField(auto_now_add=True)  # 时间

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "Comment by {0} on {1}".format(self.commentator.username, self.article)

