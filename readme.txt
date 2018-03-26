CMDB系统

基于Python2.7，Django1.8.2版本
若直接使用本sqlite文件，初始用户为admin----123.com

一、当前实现功能：
页面上标红的标签均未实现。

用户管理
  1、添加用户，用户登录、记住密码
  2、当前登录用户修改个人设置
设备管理
  服务器：
    1、添加服务器
    2、下发脚本到客户端，自动获取客户端系统信息
    3、通过gateone1.2实现WebSSH功能
  办公PC：
    1、实现办公PC增删改查
    2、办公PC实现Excel报表导出功能



二、部署依赖模块：
1、安装依赖模块
pip install -r requirements.txt

2、被添加的server客户端需安装psutil模块
pip install psutil


三、初始化数据库，包含创建默认用户

python manage.py migrate
其中User\migrations\0002_auto_20180322_2207.py 文件中包含对初始用户admin的添加。

四、部署配置Gateone
这里使用Gateone版本为1.2

1、安装Gateone

pip install --upgrade setuptools
pip install tornado==4.3
pip install Pillow

从github上下载gateone源码解压安装  https://github.com/liftoff/GateOne

cd GateOne-master/
python setup.py install

2、配置Gateone
修改运行访问范围，谁调用gateone添加谁
vim /etc/gateone/conf.d/10server.conf
"origins": ["localhost", "127.0.0.1", "centos-7-3", "192.168.1.152","192.168.1.222:8000"],

修改认证方式
默认为不认证none，我们修改为api。
vim /etc/gateone/conf.d/20authentication.conf
"auth": "api",

生成api_key和secret
执行下面命令，将会生成新的配置文件30api_keys.conf
gateone --new_api_key
api_keys 的value值，冒号前面为api_key，后面的是secret。
将这个值配置到Equipment\views.py 的get_auth_obj方法中


五、修改客户端脚本连接服务器的url
sftpDir/main.py
url修改为正确可用的。


暂时实现以上功能，后续继续迭代更新。