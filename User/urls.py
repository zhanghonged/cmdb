#coding:utf-8
from django.conf.urls import include, url
from views import *
urlpatterns = [
    url(r'^user_list/', user_list, name='user_list'),
    url(r'^user_list_data/', user_list_data, name='user_list_data'),
    url(r'^userValid/', userValid, name='userValid'),
    url(r'^user_save', user_save, name='user_save'),
    url(r'user_setting', user_setting, name='user_setting'),
    url(r'login/$',login, name='loginAuth'),
    url(r'^group_list/$', group_list, name='group_list'),
    url(r'group_add/$', group_add, name='group_add'),
    url(r'^group_detail/$', group_detail, name='group_detail'),
    url(r'^group_list_data/$', group_list_data, name='group_list_data')
]