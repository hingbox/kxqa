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
def get_date_range(start, end, step=1, format_string="%Y-%m-%d"):
        strptime, strftime = datetime.datetime.strptime, datetime.datetime.strftime
        days = (strptime(end, format_string) - strptime(start, format_string)).days
        return [strftime(strptime(start, format_string) + datetime.timedelta(i), format_string) for i in xrange(0, days, step)]
date_list = get_date_range('2018-01-01','2018-01-02',1)
pages=[]
for d in date_list:
    for i in range(1,5):
        url = 'www'+d
        pages.append(url)
#return pages
print pages

print('111',datetime.datetime.now().strftime("%Y-%m-%d"))
# start_urls = []
#     for page in range(1, 71):# -- 71
#         for record in range(1,5):
#             urls = 'http://app.cnfol.com/qualityarticles/qualityarticles.php?CatId=101&starttime='+str(timestamp)+'&endtime='+str(timestamp)+'&num='+str(num)+'&page='+str(page)+'&record='+str(record)+'&jsoncallback=callback&_='+str(millis)
#             start_urls.append(urls)