#coding:utf-8
import random
from django.shortcuts import render, redirect
from django.db import connection

content = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz'
# def base(request):
#     return render(request,'base.html',locals())

def login(request):
    '''
    登录页面，随机生成字符串设置cookie并传到前端页面
    :param request:
    :return:
    '''
    v_data = "".join(random.sample(content, 28))
    # 将v_data传到前端页面
    response =  render(request, 'login.html',{'v_data':v_data})
    response.set_cookie('token',v_data)
    return response

def logout(request):
    isLogin = request.session.get('isLogin',False)
    if isLogin:
        request.session.flush()
    return redirect('login')

def getpage(sql, page, num = 12, maxpage_num = 7):
    '''
    查询数据库数据
    :param sql: 每次查询的语句
    :param page: 当前的页码
    :param num: 每页数据的条数
    :param maxpage_num: 分页区域显示的页码数量
    :return:查询出来的数据和分页信息
    '''
    page = int(page)
    num = int(num)
    start_page = (page-1) * num
    page_data_sql = sql + ' limit %s,%s'%(start_page,num)
    print page_data_sql
    cursor = connection.cursor() #实例化游标
    cursor.execute(page_data_sql)
    page_data = cursor.fetchall()

    desc = cursor.description #取出表的字段值
    # 把表地段和数据拼接为字典个数，存放到list里
    data_list = [
        dict(zip([d[0] for d in desc],row))
        for row in page_data
    ]
    #查询总条数
    page_total_sql = 'select count(f.id) from (%s) as f'%sql
    cursor.execute(page_total_sql)
    nums = cursor.fetchone()[0]
    #页码最大值
    if nums%num == 0:
        page_total = nums/num
    else:
        page_total = nums/num + 1

    #最多页码显示范围
    part = maxpage_num/2
    if page_total < maxpage_num:
        page_range = [i for i in range(1,page_total+1)]
    elif page <= part:
        page_range = [i for i in range(1,maxpage_num+1)]
    elif page + part > page_total:
        page_range = [i for i in range(page_total-maxpage_num,page_total+1)]
    else:
        page_range = [i for i in range(page-part,page+part+1)]

    result = {
        'page_data':data_list,
        'page_range':page_range,
        'current_page':page,
        'max_page':page_total
    }
    return result

def loginValid(fun):
    '''
    cookie校验装饰器
    :param request:
    :return:
    '''
    def inner(request, *args, **kwargs):
        isLogin = request.session.get('isLogin',False)
        # 根据浏览器cookie里存储的sessionid在session表里查看登录状态
        if isLogin:
            return fun(request, *args, **kwargs)
        else:
            return redirect('login')
    return inner