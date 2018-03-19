#coding:utf-8
import re
from django import forms
from django.forms import ValidationError
from models import CMDBUser


class Register(forms.Form):
    '''
    添加用户表单
    '''
    username = forms.CharField(
        max_length=32,
        min_length=6,
        label='用户名',
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'用户名'})
    )
    password = forms.CharField(
        max_length=32,
        min_length=6,
        label='密码',
        widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'密码'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = CMDBUser.objects.get(username=username)
        except:
            return username
        else:
            raise ValidationError('用户名已存在')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password.isdigit():
            raise ValidationError('密码不可以完全由数字组成')
        elif password.isalnum():
            raise ValidationError('密码不可以完全由数字字母组成')
        else:
            return password

class UserSetting(forms.Form):
    '''
    用户个人设置表单
    '''
    phone = forms.CharField(
        max_length = 11,
        min_length = 11,
        label = '手机号',
        required = False,
        widget = forms.TextInput(attrs={'class':'form-control','placeholder':'手机号'})
    )
    email = forms.EmailField(
        label = '邮箱',
        required = False
    )
    photo = forms.ImageField(
        label = '头像',
        required = False
    )
    def clean_email(self):
        '''
        检测邮箱格式及是否重复
        :return:
        '''
        email = self.cleaned_data.get('email')
        res = re.match(r"\w+@\w+\.\w+",email)
        if res:
            return email
        else:
            raise ValidationError('请输入正确邮箱')
    # def clean_email(self):
    #     '''
    #     检测邮箱格式及是否重复
    #     :return:
    #     '''
    #     email = self.cleaned_data.get('email')
    #     res = re.match(r"\w+@\w+\.\w+",email)
    #     if res:
    #         try:
    #             user = CMDBUser.objects.get(email = email)
    #         except:
    #             return email
    #         else:
    #             raise ValidationError('邮箱已存在')
    #     else:
    #         raise ValidationError('请输入正确邮箱')
    # def clean_phone(self):
    #     '''
    #     检查手机号是否重复
    #     :return:
    #     '''
    #     phone = self.cleaned_data.get('phone')
    #     try:
    #         user = CMDBUser.objects.get(phone=phone)
    #     except:
    #         return phone
    #     else:
    #         raise ValidationError('手机号已存在')