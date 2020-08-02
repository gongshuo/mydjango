from . import models
from django.contrib.auth.models import User


def add_data1():  # blog_articles 插入数据
    u = User.objects.filter(id=1).first()
    a = models.BlogArticles(author=u, title='hello', body='lalala')
    a.save()
    """以下为参考代码"""
    # d1 = DepartmentInfo.objects.get(depart_id=1)  # d1表示UserInfo的外键数据
    # r1 = Role.objects.get(role_name=role)  # r1表示UserInfo的多对多数据
    # u1 = UserInfo(user_name=name, user_pwd=password, sex=sex, mobileno=mobile, email=email, depart=d1)
    # u1.save()
    # u1.role.add(r1)  # 多对多关系,一对多关系，一对一关系都可
    # u1.save()
