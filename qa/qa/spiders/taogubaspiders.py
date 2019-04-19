#!/usr/bin/env python
# -*- coding:utf-8 -*-
#encoding=utf-8
'''
@描述：PyCharm
@作者：hingbox
@邮箱：hingbox@163.com
@版本：V1.0
@文件名称 : taogubaspiders.py
@创建时间：2018/8/25 21:59
'''
import scrapy
from scrapy.http.request import Request
'''
淘股吧
'''
class taogubaSpiders(scrapy.Spider):
    # name = 'login_spider'
    # start_urls = ['http://www.login.com']
    #
    # def parse(self, response):
    #     return [
    #         scrapy.FormRequest.from_response(
    #                 response,
    #                 # username和password要根据实际页面的表单的name字段进行修改
    #                 formdata={'username': 'your_username', 'password': 'your_password'},
    #                 callback=self.after_login)]
    # def after_login(self, response):
    #     # 登录后的代码
    #     pass
    name = "taoguba"
    allowed_domains = ["taoguba.com.cn"]
    start_urls = [
        "https://www.taoguba.com.cn/index?pageNo=10000&blockID=1&flag=0&pageNum=10000",
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, cookies={
                'UM_distinctid': '164d561807015d-079f09bf7786cb-47e1039-100200-164d56180711e4',
                'tgbuser': '2882972',
                'CNZZDATA1574657': 'cnzz_eid%3D595931164-1532583112-%26ntime%3D1535201008',
                'Hm_lvt_cc6a63a887a7d811c92b7cc41c441837': '1532942011,1534383535,1534730310,1535205133',
                'Hm_lpvt_cc6a63a887a7d811c92b7cc41c441837': '1535205166'
            }, callback=self.parse)

    def parse(self, response):
        print('==========', response.body)


