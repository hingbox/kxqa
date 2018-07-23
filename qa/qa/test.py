#!/usr/bin/env python
# -*- coding:utf-8 -*-
#encoding=utf-8
'''
@描述：PyCharm
@作者：hingbox
@邮箱：hingbox@163.com
@版本：V1.0
@文件名称 : test.py
@创建时间：2018/7/23 15:34
'''
import datetime
import re
print(datetime.datetime.now()-datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
str = "07月17日 17:42"
strs = '18分钟前'
strss = '16小时前'

print('bb',re.search(r'分钟',strs))
print('mmm',re.search('前',strs))
print('hhh',strss.find('小时前'))
print re.findall(r"\d+\.?\d*",strss)
print ('==strs',strs[0:1])
a = "吉比特(603444)"
print(a.split('(')[1])

print (datetime.datetime.now()-datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")