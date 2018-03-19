#coding:utf-8
from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'^server_list/', server_list, name='server_list'),
    url(r'^server_list_data', server_list_data, name='server_list_data'),
    url(r'^server_add', server_add, name='server_add'),
    url(r'^server_save', server_save, name='server_save'),
    url(r'^gateone', gateone, name='gateone'),
    url(r'^get_auth_obj',get_auth_obj, name='get_auth_obj'),
    url(r'^pc_list/$', pc_list, name='pc_list'),
    url(r'^pc_add/$', pc_add, name='pc_add'),
    url(r'^pc_list_data/$', pc_list_data, name='pc_list_data'),
    url(r'^pc_edit/$', pc_edit, name='pc_edit'),
    url(r'pc_del/$', pc_del, name='pc_del'),
    url('^aaa',linshi)
]