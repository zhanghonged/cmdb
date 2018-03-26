#coding:utf-8
import json
import time
import paramiko
import hmac ,hashlib
from django.http import StreamingHttpResponse
from django.shortcuts import render,redirect,HttpResponse
from User.models import CMDBUser
from django.http import JsonResponse
from models import Equipment,Pc
from cmdb.views import getpage, to_excel, loginValid
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@loginValid
def server_list(request):
    '''
    服务器列表展示
    :param request:
    :return:
    '''
    uid = request.COOKIES.get('id')
    user = CMDBUser.objects.get(id = uid)
    return render(request,'serverlist.html',locals())

def server_list_data(request):
    '''
    :param request:
    :return:json类型返回服务器信息分页数据
    '''
    if request.method == 'GET':
        page = request.GET.get('page')
        num = request.GET.get('num')
        sql = 'select * from Equipment_equipment'
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
    return JsonResponse(result)

def connect_server(ip,port,user,password):
    '''
    通过paramiko检测服务器是否可以连通，是的话返回连接对象
    :param ip:
    :param port:
    :param user:
    :param password:
    :return:返回连接对象
    '''
    result = {'status':'error','data':''}
    try:
        trans = paramiko.Transport(ip,port)
        trans.connect(username = user, password = password)
    except Exception as e:
        result['data'] = str(e)
    else:
        result['status'] = 'success'
        result['data'] = trans
    finally:
        return result

def server_add(request):
    '''
    服务器添加方法，根据ip、port、username、password对服务器操作：远程登录、脚本上传、脚本远程执行
    :param request:
    :return:
    '''
    result = {'status':'error','data':''}
    if request.method == 'POST':
        ip = request.POST.get('ip')
        port = request.POST.get('port')
        username = request.POST.get('username')
        password = request.POST.get('password')
        print ip,port,username,password
        if ip and port and username and password:
            #save db
            equipment = Equipment()
            equipment.ip = ip
            equipment.port = port
            equipment.username = username
            equipment.password = password
            equipment.save()
            #连接远程虚拟机
            connect = connect_server(ip,port,username,password)
            if connect['status'] == 'success':
                trans = connect['data']
                # 用于文件上传和下载的sftp服务
                sftp = paramiko.SFTPClient.from_transport(trans)
                # 远程执行命令服务
                ssh = paramiko.SSHClient()
                ssh._transport = trans
                # 创建目录
                stdin,stdout,stderr = ssh.exec_command('mkdir CMDBClient')
                time.sleep(1)
                # 上传文件
                sftp.put('sftpDir/getData.py','CMDBClient/getData.py')
                sftp.put('sftpDir/sendData.py', 'CMDBClient/sendData.py')
                sftp.put('sftpDir/main.py', 'CMDBClient/main.py')
                # 调用脚本
                stdin,stdout,stderr = ssh.exec_command('python CMDBClient/main.py')
                trans.close()
                # 连接成功状态记录到数据库
                equipment = Equipment.objects.get(ip=ip)
                equipment.status = 'True'
                equipment.save()
                result['status'] = 'success'
                result['data'] = '添加成功'
            else:
                result['data'] = connect['data']
                # 连接失败状态记录到数据库
                equipment = Equipment.objects.get(ip = ip)
                equipment.status = 'False'
                equipment.save()
        else:
            result['data'] = '添加失败，ip port username password不能为空'
    else:
        result['data'] = '添加失败，请求类型必须为POST类型'
    return JsonResponse(result)

# 由于客户端调用此接口，去掉csff验证
@csrf_exempt
def server_save(request):
    '''
    接收服务器发过来的系统信息，报错入库
    :param request:
    :return:
    '''
    result = {'status':'error','data':''}
    ip = request.META['REMOTE_ADDR']
    if request.method == 'POST':
        hostname = request.POST.get('get_hostname')
        sys_version = request.POST.get('get_systemVersion')
        mac = request.POST.get('get_mac')
        sys_type = request.POST.get('get_systeType')
        memory = request.POST.get('get_memory')
        cpu = request.POST.get('get_cpu')
        disk = request.POST.get('get_disk')

        try:
            equipment = Equipment.objects.get(ip=ip)
        except Exception ,e:
            print e
            result['data'] = str(e)
        else:
            equipment.hostname = hostname
            equipment.sys_version = sys_version
            equipment.mac = mac
            equipment.sys_type = sys_type
            equipment.memory = memory
            equipment.cpu = cpu
            equipment.disk = disk
            equipment.save()
            result["statue"] = "success"
            result["data"] = "your data is saved"
    else:
        result['data'] = 'request must be post'
    return JsonResponse(result)

@loginValid
def pc_list(request):
    return render(request,'pclist.html',locals())

def pc_list_data(request):
    '''
    查询数据库数据以json格式返回
    :param request:
    :return:
    '''
    if request.method == 'GET':
        page = request.GET.get('page')
        num = request.GET.get('num')
        keyword = request.GET.get('search','').strip()
        #print type(keyword)
        #print keyword
        if keyword:
            sql = (
                  "select * from Equipment_pc"
                  " where Equipment_pc.user LIKE" +" '%" + keyword + "%'"
                  " or Equipment_pc.ip LIKE " +" '%" + keyword + "%'"
                  " or Equipment_pc.mac LIKE" +" '%" + keyword + "%'"
                  " or Equipment_pc.cpu LIKE" + " '%" + keyword + "%'"
                  " or Equipment_pc.memory LIKE" + " '%" + keyword + "%'"
                  " or Equipment_pc.disk LIKE" + " '%" + keyword + "%'"
                  " or Equipment_pc.display LIKE" + " '%" + keyword + "%'"
                  " or Equipment_pc.department LIKE" + " '%" + keyword + "%'"
                  " or Equipment_pc.note LIKE" + " '%" + keyword + "%'"
            )
            #print sql
        else:
            sql = 'select * from Equipment_pc'
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

def pc_add(request):
    '''
    添加个人pc
    :param request:
    :return:
    '''
    result = {'status':'error','data':''}
    if request.method == 'POST':
        print request.POST
        user = request.POST.get('user')
        ip = request.POST.get('ip')
        mac = request.POST.get('mac')
        cpu = request.POST.get('cpu')
        disk = request.POST.get('disk')
        memory = request.POST.get('memory')
        display = request.POST.get('display')
        department = request.POST.get('department')
        note = request.POST.get('note')
        if ip and user:
            try:
                # 检测此ip是否已经存在
                pc = Pc.objects.get(ip = ip)
            except:
                # 不存在入库
                Pc.objects.create(
                    user = user,
                    ip = ip,
                    mac = mac,
                    cpu = cpu,
                    disk = disk,
                    memory = memory,
                    display = display,
                    department = department,
                    note = note
                )
                result['status'] = 'success'
                result['data'] = '添加成功'
            else:
                result['data'] = 'IP已存在'
        else:
            result['data'] = '使用者和IP不能为空'
    else:
        result['data'] = '必须是POST请求'
    return JsonResponse(result)

def pc_edit(request):
    result = {'status':'error','data':{},'message':''}
    # 如果是get请求，返回当前pc的数据，用于vue前台默认展示
    if request.method == 'GET':
        pid = request.GET.get('pid')
        if pid:
            try:
                pc = Pc.objects.get(id=pid)
            except Exception as e:
                print e
            else:
                result['data']['id'] = pc.id
                result['data']['user'] = pc.user
                result['data']['ip'] = pc.ip
                result['data']['mac'] = pc.mac
                result['data']['cpu'] = pc.cpu
                result['data']['disk'] = pc.disk
                result['data']['memory'] = pc.memory
                result['data']['display'] = pc.display
                result['data']['department'] = pc.department
                result['data']['note'] = pc.note
                result['status'] = 'success'
        else:
            result['message'] = 'error'
    # 如果是post请求，则为修改数据
    elif request.method == 'POST':
        pid = request.POST.get('pid')
        user = request.POST.get('user')
        ip = request.POST.get('ip')
        mac = request.POST.get('mac')
        cpu = request.POST.get('cpu')
        disk = request.POST.get('disk')
        memory = request.POST.get('memory')
        display = request.POST.get('display')
        department = request.POST.get('department')
        note = request.POST.get('note')
        if pid:
            try:
                pc = Pc.objects.get(id = pid)
            except Exception as e:
                print e
            else:
                # 判断除此用户外，ip是否已存在
                pc_list = Pc.objects.filter(ip = ip).exclude(id=pid)
                # 如果pc_list长度大于0，说明此ip已存在
                if len(pc_list) > 0:
                    result['message'] = '修改失败，IP已存在，请确认'
                else:
                    pc.user=user
                    pc.ip=ip
                    pc.mac=mac
                    pc.cpu=cpu
                    pc.disk=disk
                    pc.memory=memory
                    pc.display=display
                    pc.department=department
                    pc.note=note
                    pc.save()
                    result['status'] = 'success'
                    result['message'] = '修改成功'
        else:
            result['message'] = '修改失败，请联系管理员'
    return JsonResponse(result)

def pc_del(request):
    result = {'status':'error','data':''}
    if request.method == 'GET':
        pid = request.GET.get('pid')
        if pid:
            try:
                Pc.objects.get(id = pid).delete()
            except Exception as e:
                result['data'] = str(e)
            else:
                result['status'] = 'success'
                result['data'] = '删除成功'
        else:
            result['data'] = '设备ID不存在'
    return JsonResponse(result)

@loginValid
def gateone(request,id):
    id = int(id)
    server = Equipment.objects.get(id = id)
    ip = server.ip
    port = server.port
    username = server.username
    return render(request,'gateone.html',locals())

def create_signature(secret,*parts):
    '''
    此方法主要用来加密
    :param secret:
    :param parts:
    :return:
    '''
    hash = hmac.new(secret, digestmod=hashlib.sha1)
    for part in parts:
        hash.update(str(part))
    return hash.hexdigest()

def get_auth_obj(request):
    '''
    gateone继承到web界面上
    :param request:
    :return:返回gateone url及认证参数
    '''
    # 安装gateone的服务器以及端口.
    gateone_server = 'https://192.168.1.152:443'
    # 之前生成的api_key 和secret
    api_key = 'NGUzYzU2ZWRiYTM3NDUzMjk4OGI5MWQ4ZGNhNDUzMjBmN'
    secret = 'NjNkNWRlZWI3OWVhNDY0YmIyYzU4ODA4MDQyYzgyNmJkM'
    authobj = {
        'api_key':api_key,
        'upn':'gateone',
        'timestamp':str(int(time.time() * 1000)),
        'signature_method':'HMAC-SHA1',
        'api_version':'1.0'
    }
    authobj['signature'] = create_signature(secret,authobj['api_key'],authobj['upn'],authobj['timestamp'])
    auth_info_and_server = {'url':gateone_server,'auth':authobj}
    return JsonResponse(auth_info_and_server)


def file_iterator(filename, chunk_size=512):
    '''
    读取文件迭代器
    :param filename:
    :param chunk_size:
    :return:
    '''
    with open(filename, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break

def export_pc(request):
    '''
    导出excel报表功能
    :param request:
    :return:
    '''
    if request.method == 'GET':
        keyword = request.GET.get('search')
        temp_file = 'PC%s.xlsx'%time.strftime('%Y%m%d',time.localtime())
        #sql = 'select * from Equipment_pc'
        sql = (
            "select * from Equipment_pc"
            " where Equipment_pc.user LIKE" + " '%" + keyword + "%'"
            " or Equipment_pc.ip LIKE " + " '%" + keyword + "%'"
            " or Equipment_pc.mac LIKE" + " '%" + keyword + "%'"
            " or Equipment_pc.cpu LIKE" + " '%" + keyword + "%'"
            " or Equipment_pc.memory LIKE" + " '%" + keyword + "%'"
            " or Equipment_pc.disk LIKE" + " '%" + keyword + "%'"
            " or Equipment_pc.display LIKE" + " '%" + keyword + "%'"
            " or Equipment_pc.department LIKE" + " '%" + keyword + "%'"
            " or Equipment_pc.note LIKE" + " '%" + keyword + "%'"
        )
        result = to_excel(sql,temp_file)
        # Excel文件导出成功，开始下载文件
        if result['status'] == 'success':
            the_file_name = temp_file
            response = StreamingHttpResponse(file_iterator(the_file_name))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
            return response
        else:
            return JsonResponse(result)

def get_mac():
    import random
    temp = '1234567890ABCDEF'
    a=''
    for i in range(6):
       a+=''.join(random.sample(temp,2))
    mac = ':'.join(a[e:e+2] for e in range(0,11,2))
    return mac

def linshi(request):
    import random
    names = ['张玉宁','于汉超','郜林','范志毅','曾诚','郝海东','李金玉','江洪']
    cpus = ['i5-3450 CPU @ 3.10GHz','i5-3450 CPU @ 3.10GHz','inter-core 2.7','AMD@3.8速龙']
    memorys = ['1GB','2GB','3GB','4GB','8GB','16GB','32GB','64GB']
    departments = ['宙合', '译喵', '财务']
    for i in xrange(100):
        Pc.objects.create(
            user=random.choice(names)+str(i),
            ip='192.168.100.%s'%i,
            mac = get_mac(),
            cpu = random.choice(cpus),
            memory = random.choice(memorys),
            disk = '',
            department = random.choice(departments),
            note = ''
        )
    return JsonResponse({'status':'success'})
