from django.db import models
from django.contrib.auth.models import User
# Create your models here.
# account_userinfo 表，其中记录了school、company、profession、address、aboutme字段内容。
# account_userprofile 表，其中记录了phone、birth字段内容。
# auth_user 表，这是Django默认的，其中记录了password、last_login、si_supperuser、first_name、last_name、email、username等字段内容。


class UserProfile(models.Model):
    """补充User表不足的地方"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)  # 唯一键
    birth = models.DateField(blank=True, null=True)     # 可以为空,也可以为null
    phone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return 'user {}'.format(self.user.username)


class UserInfo(models.Model):
    """补充User表不足的地方"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    school = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    aboutme = models.TextField(blank=True)
    photo = models.ImageField(blank=True)   # 图片

    def __str__(self):
        return "user:{}".format(self.user.username)