#!/usr/bin/python
# coding:utf-8

import urllib, urllib2


class Sender:
    def __init__(self,url,data):
        self.url = url
        #urllib.urlencode方法会自动将data类型转换为json
        self.data = urllib.urlencode(data)
    def get_request(self):
        self.request = urllib2.Request(self.url,data=self.data)
    def get_response(self):
        self.response = urllib2.urlopen(self.request)
        result = self.response.read()
        return result
