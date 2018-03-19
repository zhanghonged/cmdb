#coding:utf-8
import hashlib
from PIL import Image
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from forms import Register, UserSetting
from models import CMDBUser
from cmdb.views import getpage ,loginValid
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@loginValid
def index(request):
    uid = request.COOKIES.get('id')
    user = CMDBUser.objects.get(id = uid)
    return render(request,'index.html',{'user':user})

@loginValid
def user_list(request):
    '''
    :param request:
    :return: 用户管理页
    '''
    uid = request.COOKIES.get('id')
    user = CMDBUser.objects.get(id=uid)
    register = Register
    return render(request,'userlist.html',locals())

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
                'max_page': ''
            }
    else:
        result = {
            'page_data': '',
            'page_range': '',
            'current_page': '',
            'max_page': ''
        }
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
            print '表单校验成功:',obj.cleaned_data
            username = obj.cleaned_data['username']
            password = getmd5(obj.cleaned_data['password'])
            # 入库
            try:
                CMDBUser.objects.create(username=username,password=password)
            except Exception as e:
                print e
                result['data'] = '注册失败'
            else:
                result['status'] = 'success'
                result['data'] = '用户注册成功'

        else:
            print '表单校验失败:',obj.errors
            result['data'] = '注册失败'
    return JsonResponse(result)

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
