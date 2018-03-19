#coding:utf-8
from django.db import models

class CMDBUser(models.Model):
    username = models.CharField(max_length=32,verbose_name='用户名')
    password = models.CharField(max_length=32,verbose_name='密码')
    email = models.EmailField(verbose_name='邮箱',blank=True,null=True)
    phone = models.CharField(max_length=32,verbose_name='手机号',blank=True,null=True)
    photo = models.ImageField(upload_to='images',verbose_name='头像',blank=True,null=True)
    #ImageField 必须在安装pil或pillow的基础上使用
    def __unicode__(self):
        return self.username

class Permission(models.Model):
    name = models.CharField(max_length=32,verbose_name='权限名称')
    obj_id = models.IntegerField(verbose_name='操作对象')
    description = models.TextField(verbose_name='权限描述')

    def __unicode__(self):
        return self.name

class CMDBGroup(models.Model):
    name = models.CharField(max_length=32,verbose_name='组名称')

    def __unicode__(self):
        return self.name

## 关系表
class User_group(models.Model):
    user_id = models.IntegerField(verbose_name='用户ID')
    group_id = models.IntegerField(verbose_name='组ID')

class User_permission(models.Model):
    user_id = models.IntegerField(verbose_name='用户ID')
    permission_id = models.IntegerField(verbose_name='权限ID')

class Permission_group(models.Model):
    permission_id = models.IntegerField(verbose_name='权限ID')
    group_id = models.IntegerField(verbose_name='组ID')
# Create your models here.
