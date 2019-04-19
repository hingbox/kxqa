#!/usr/bin/env python
# -*- coding:utf-8 -*-
#encoding=utf-8
'''
@描述：时间封装类
@作者：hingbox
@邮箱：hingbox@163.com
@版本：V1.0
@文件名称 : dateutils.py
@创建时间：2018/7/23 17:06
'''
import datetime
import time
class DateUtils(object):
    #获取当前时间 格式为YYYY-m-d h:M:S
     def get_now_time(self):
        nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')#现在
        return nowTime
    #得到过去一个小时时间
     def get_post_time(self):
          pastTime =(datetime.datetime.now()-datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')#过去一小时时间
          return pastTime
    #得到明天的时间
     def get_tomorrow_time(self):
         tomorrowTime =(datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')#明天
         return tomorrowTime
     def get_after_tomorrow_time(self):
         afterTomorrowTime =(datetime.datetime.now()+datetime.timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')#后天
         return afterTomorrowTime

     #将10位时间戳转换为时间字符串，默认为2017-10-01 13:37:04格式
     def timestamp_to_date(self,time_stamp, format_string="%Y-%m-%d %H:%M:%S"):
        time_array = time.localtime(float(time_stamp))
        str_date = time.strftime(format_string, time_array)
        return str_date
     #将时间字符串转换为10位时间戳，时间字符串默认为2017-10-01 13:37:04格式
     def date_to_timestamp(date, format_string="%Y-%m-%d %H:%M:%S"):
        time_array = time.strptime(date, format_string)
        time_stamp = int(time.mktime(time_array))
        return time_stamp

     #不同时间格式字符串的转换
     def date_style_transfomation(date, format_string1="%Y-%m-%d %H:%M:%S",format_string2="%Y-%m-%d %H-%M-%S"):
        time_array  = time.strptime(date, format_string1)
        str_date = time.strftime(format_string2, time_array)
        return str_date

     #生成当前时间的时间戳，只有一个参数即时间戳的位数，默认为10位，输入位数即生成相应位数的时间戳，比如可以生成常用的13位时间戳
     def now_to_timestamp(digits = 10):
        time_stamp = time.time()
        digits = 10 ** (digits -10)
        time_stamp = int(round(time_stamp*digits))
        return time_stamp

     #将时间戳规范为10位时间戳
     def timestamp_to_timestamp10(time_stamp):
        time_stamp = int (time_stamp* (10 ** (10-len(str(time_stamp)))))
        return time_stamp

     # 13位时间错
     def get_timestamp13(self):
        return int(round(time.time() * 1000))

     #将当前时间转换为时间字符串，默认为2017-10-01 13:37:04格式
     def now_to_date(format_string="%Y-%m-%d %H:%M:%S"):
        time_stamp = int(time.time())
        time_array = time.localtime(time_stamp)
        str_date = time.strftime(format_string, time_array)
        return str_date

     #传入开始时间 和结束时间 返回一个时间区间列表
     def get_date_range(start, end, step=1, format_string="%Y-%m-%d"):
        strptime, strftime = datetime.datetime.strptime, datetime.datetime.strftime
        days = (strptime(end, format_string) - strptime(start, format_string)).days
        return [strftime(strptime(start, format_string) + datetime.timedelta(i), format_string) for i in xrange(0, days, step)]
    #多加一天
        print (datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    # 2018-05-09 16:56:07
    #减一天
        print (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
    # 2018-05-07 16:56:59
    #可以把days改为hours minutes，就可以提前XX小时/分钟了。

        print (datetime.datetime.now()+datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
     #13位时间戳转换为日期格式
     def timeStamp(self,timeNum):
        timeStamp = float(timeNum/1000)
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime



