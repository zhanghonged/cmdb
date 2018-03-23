#!/usr/bin/python
# coding:utf-8

from getData import GetData
from sendData import Sender


# url地址
url = 'http://192.168.1.222:8000/eq/server_save'

#采集数据
mydata = GetData()
sendData = mydata.getData()

# 发送数据
sender = Sender(url,sendData)
sender.get_request()
response = sender.get_response()

# 获取响应
print response