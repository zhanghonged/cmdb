#coding:utf-8
import hashlib
from PIL import Image
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from forms import Register, UserSetting
from models import CMDBUser,CMDBGroup,User_group
from Equipment.models import Equipment,Pc
from cmdb.views import getpage ,loginValid, getdata, logrecord


# Create your views here.
@loginValid
def index(request):
    uid = request.COOKIES.get('id')
    user = CMDBUser.objects.get(id = uid)
    serverCount = len(Equipment.objects.all())
    pcCount = len(Pc.objects.all())
    userCount = len(CMDBUser.objects.all())
    return render(request,'index.html',{'user':user,'serverCount':serverCount,'pcCount':pcCount,'userCount':userCount})

@loginValid
def user_list(request):
    '''
    :param request:
    :return: 用户管理页
    '''
    uid = request.COOKIES.get('id')
    user = CMDBUser.objects.get(id=uid)
    register = Register
    groups = CMDBGroup.objects.all()
    return render(request,'userlist.html',locals())

def get_userGroup(uid):
    '''
    根据用户id查询当前用户的属组
    :param uid:
    :return:
    '''
    result={'status':'error','data':''}
    try:
        obj = User_group.objects.get(user_id=uid)
    except Exception as e:
        result['data'] = str(e)
    else:
        gid = obj.group_id
        try:
            group = CMDBGroup.objects.get(id = gid)
        except Exception as e:
            result['data'] = str(e)
        else:
            groupname = group.name
            result['status'] = 'success'
            result['data'] = groupname
    return result

@loginValid
def user_list_data(request):
    '''
    从数据库查询分页用户数据
    :param request:
    :return:json类型用户分页数据
    '''
    if request.method == 'GET':
        page = request.GET.get('page')
        num = request.GET.get('num')
        sql = 'select * from User_cmdbuser'
        if page and num:
            result = getpage(sql,page,num)
        elif page:
            result = getpage(sql,page)
        else:
            result = {
                'page_data': '',
                'page_range': '',
                'current_page': '',
                'max_page': '',
                'page_num':''
            }
    else:
        result = {
            'page_data': '',
            'page_range': '',
            'current_page': '',
            'max_page': '',
            'page_num':''
        }
    # 获取用户组信息
    group_sql = 'select * from User_cmdbgroup'
    group_result = getdata(group_sql)
    result['groupData'] = group_result

    # 获取当前用户的属组信息
    for u in result['page_data']:
        res = get_userGroup(u['id'])
        if res['status'] == 'success':
            u['groupname'] = res['data']

    return JsonResponse(result)

def userValid(request):
    '''
    验证用户名是否已经注册
    :param request:
    :return:返回json对象
    '''
    result = {'valid':False}
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            try:
                u = CMDBUser.objects.get(username=username)
            except:
                result['valid'] = True
    return JsonResponse(result)

def getmd5(password):
    '''
    密码加密
    :param password: 用户输入的密码
    :return: 加密后的字符串
    '''
    md5 = hashlib.md5()
    md5.update(password)
    return md5.hexdigest()

#@loginValid
@logrecord
def user_save(request):
    '''
    注册用户
    :param request:
    :return:
    '''
    result = {'status':'error','data':''}
    if request.method == 'POST':
        obj = Register(request.POST)
        if obj.is_valid():
            #print '表单校验成功:',obj.cleaned_data
            username = obj.cleaned_data['username']
            password = getmd5(obj.cleaned_data['password'])
            groupname = request.POST.get('groupname')

            try:
                # 用户入库
                u= CMDBUser(username=username,password=password)
                u.save()
                uid = u.id
            except Exception as e:
                print e
                result['data'] = '添加用户失败'
            else:
                try:
                    # 判断用户提交的组是否存在
                    g = CMDBGroup.objects.get(name=groupname)
                    gid = g.id
                except Exception as e:
                    result['data'] = str(e)
                else:
                    try:
                        # 用户组关系入库
                        User_group.objects.create(user_id=uid,group_id=gid )
                    except Exception as e:
                        result['data'] = str(e)
                    else:
                        result['status'] = 'success'
                        result['data'] = '添加用户成功'

        else:
            print '表单校验失败:',obj.errors
            result['data'] = '添加用户失败'
    return JsonResponse(result)

@loginValid
@logrecord
def user_edit(request):
    result = {'status': 'error', 'data': ''}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        groupname = request.POST.get('groupname')
        id = request.POST.get('id')
        if username and password and id:
            try:
                # 判断用户id是否存在
                u = CMDBUser.objects.get(id = id)
                uid = u.id
            except Exception as e:
                result['data'] = str(e)
            else:
                # 判断用户提交的组是否存在
                try:
                    g = CMDBGroup.objects.get(name=groupname)
                    gid = g.id
                except Exception as e:
                    result['data'] = str(e)
                else:
                    # 判断用户密码，如果和数据库不同，则加密入库，否则不处理
                    if u.password != password:
                        #判断密码复杂性要求
                        if password.isdigit():
                            result['data'] = '编辑失败，密码不可以完全由数字组成'
                        elif password.isalnum():
                            result['data'] = '编辑失败，密码不可以完全由数字字母组成'
                        else:
                            # 用户密码修改入库
                            u.password = getmd5(password)
                            u.save()

                    # 用户组关系修改入库
                    # 如果当前用户有组就修改，否则添加
                    try:
                        obj = User_group.objects.get(user_id=uid)
                    except:
                        User_group.objects.create(user_id=uid,group_id=gid)
                    else:
                        obj.group_id = gid
                        obj.save()
                    finally:
                        result['status'] = 'success'
                        result['data'] = '编辑成功'
        else:
            result['data'] = '编辑失败，字段不能为空'
    else:
        result['data'] = '编辑失败，必须为POST请求'
    return JsonResponse(result)

@loginValid
@logrecord
def user_del(request):
    result = {'status':'error','data':''}
    if request.method == 'GET':
        uid = request.GET.get('uid')
        if uid:
            try:
                CMDBUser.objects.get(id = uid).delete()
                User_group.objects.get(user_id=uid).delete()
            except Exception as e:
                result['data'] = str(e)
            else:
                result['status'] = 'success'
                result['data'] = '删除成功'
        else:
            result['data'] = '用户ID不存在'
    return JsonResponse(result)

@loginValid
@logrecord
def user_setting(request):
    '''
    用户个人设置
    :param request:
    :return:
    '''
    result = {'status':'error','data':''}
    if request.method == 'POST':
        #把ajax 传过来的POST和FILES传给表单去校验，这样图片文件就可以向普通字段那样直接入库，并自动保存文件到服务器
        # 如果不经过表单处理，则图片文件需要手动处理
        # 处理图片信息
        #from PIL import Image
        # photo = request.FILES.get('photo')
        # name = 'static/images/' + photo.name
        # #保存图片
        # img = Image.open(photo)
        # img.save(name)
        #在cookie中获取用户id
        uid = request.COOKIES.get('id')
        obj = UserSetting(request.POST,request.FILES)
        if obj.is_valid():
            #print '校验成功：',obj.cleaned_data
            phone = obj.cleaned_data['phone']
            email = obj.cleaned_data['email']
            photo = obj.cleaned_data['photo']

            #判断电话是否已存在
            user_list = CMDBUser.objects.filter(phone=phone).exclude(id = uid)
            #除此用户外其他用户已经存在此手机号
            if len(user_list) > 0:
                result['data'] = '手机号已存在'
            else:

                user_list_1 = CMDBUser.objects.filter(email=email).exclude(id=uid)
                # 除此用户外其他用户已经存在此邮箱
                if len(user_list_1) > 0:
                    result['data'] = '邮箱已存在'
                #开始入库
                else:
                    try:
                        user = CMDBUser.objects.get(id = uid)
                    except:
                        result['data'] = '提交错误'
                    else:
                        user.phone = phone
                        user.email = email
                        user.photo = photo
                        user.save()
                        result['status'] = 'success'
                        result['data'] = '保存成功'
        else:
            print '校验失败：',obj.errors
            result['data'] = '数据校验失败'
    else:
        result['data'] = '请求方式错误'
    print result
    return JsonResponse(result)

@logrecord
def login(request):
    '''
    登录验证
    :param request:
    :return:
    '''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        loginvalid = request.POST.get('loginvalid')
        token_cookie = request.COOKIES.get('token')
        remember = request.POST.get('remember')
        # 判断前端页面的值与token_cookie的值是否相同，这是一种反爬手段
        if loginvalid == token_cookie:
            try:
                user = CMDBUser.objects.get(username=username)
            except:
                #重定向到url别名login
                return redirect('login')
            else:
                if user.password == getmd5(password):
                    response = redirect('index')
                    response.set_cookie('id',user.id)
                    request.session['isLogin'] = True
                    request.session['nname'] = username

                    # 记住密码写入cookie，设置有效期为7天
                    if remember == 'Remember-me':
                        response.set_cookie('remUser',True,604800)
                        response.set_cookie('username',username,604800)
                        response.set_cookie('password',password,604800)
                    else:
                        response.delete_cookie('remUser')
                        response.delete_cookie('username')
                        response.delete_cookie('password')
                    return response
                else:
                    return redirect('login')
        else:
            return redirect('login')
    return redirect('login')

@loginValid
def group_list(request):
    '''
    用户组管理页
    :param request:
    :return:
    '''
    uid = request.COOKIES.get('id')
    user = CMDBUser.objects.get(id=uid)
    register = Register
    return render(request,'usergroups.html',locals())

@loginValid
def group_add_page(request):
    if request.method == 'GET':
        id = request.GET.get('gid')
        if id:
            group = CMDBGroup.objects.get(id=id)
    return render(request,'groupadd.html',locals())

@loginValid
def group_list_data(request):
    if request.method == 'GET':
        page = request.GET.get('page')
        num = request.GET.get('num')
        sql = 'select * from User_cmdbgroup'
        if page and num:
            result = getpage(sql,page,num)
        elif page:
            result = getpage(sql,page)
        else:
            result = {
                'page_data': '',
                'page_range': '',
                'current_page': '',
                'max_page': '',
                'page_num':''
            }
    else:
        result = {
            'page_data': '',
            'page_range': '',
            'current_page': '',
            'max_page': '',
            'page_num': ''
        }
    return JsonResponse(result)

@loginValid
@logrecord
def group_add(request):
    result = {'status':'error','data':''}
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            try:
                group = CMDBGroup.objects.get(name=name)
            except:
                CMDBGroup.objects.create(name=name,description=description)
                result['status'] = 'success'
                result['data'] = '新建组成功'
            else:
                result['data'] = '新建组失败，组名已存在'
        else:
            result['data'] = '新建组失败，无法获取组名'
    else:
        result['data'] = '新建组失败,必须为POST请求方式'

    print result
    return JsonResponse(result)

@loginValid
@logrecord
def group_edit(request):
    result = {'status':'error','data':''}
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        id = request.POST.get('gid')
        if id:
            try:
                group = CMDBGroup.objects.get(id=id)
            except Exception as e:
                result['data'] = str(e)
            else:
                groupList = CMDBGroup.objects.filter(name = name).exclude(id = id)
                if len(groupList) > 0:
                    result['data'] = '编辑组失败,组名已存在'
                else:
                    group.name = name
                    group.description = description
                    group.save()
                    result['status'] = 'success'
                    result['data'] = '修改成功'
        else:
            result['data'] = '编辑组失败，无法获取组名'
    else:
        result['data'] = '编辑组失败,必须为POST请求方式'
    return JsonResponse(result)

@loginValid
@logrecord
def group_del(request):
    result = {'status':'error','data':''}
    if request.method == 'GET':
        id = request.GET.get('gid')
        if id:
            try:
                CMDBGroup.objects.get(id=id).delete()
                User_group.objects.filter(group_id=id).delete()
            except Exception as e:
                result['data'] = e
            else:
                result['status'] = 'success'
                result['data'] = '删除成功'
        else:
            result['data'] = '组ID不存在'
    return JsonResponse(result)

@loginValid
def user_logs(request):
    uid = request.COOKIES.get('id')
    user = CMDBUser.objects.get(id=uid)
    return render(request,'userlogs.html',locals())

@loginValid
def user_logs_data(request):
    if request.method == 'POST':
        page = request.POST.get('page')
        num = request.POST.get('num')
        keyword = request.POST.get('search', '').strip().encode('utf8')

        if keyword:
            sql = (
                  "select * from User_user_logs"
                  " where User_user_logs.username LIKE" +" '%" + keyword + "%'"
                  " or User_user_logs.action LIKE " +" '%" + keyword + "%'"
            )
        else:
            sql = 'select * from User_user_logs'
        if page and num:
            result = getpage(sql,page,num)
        elif page:
            result = getpage(sql,page)
        else:
            result = {
                'page_data': '',
                'page_range': '',
                'current_page': '',
                'max_page': '',
                'page_num':''
            }
    else:
        result = {
            'page_data': '',
            'page_range': '',
            'current_page': '',
            'max_page': '',
            'page_num': ''
        }
    return JsonResponse(result)