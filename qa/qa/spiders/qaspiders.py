#!/usr/bin/env python
# -*- coding:utf-8 -*-
#encoding=utf-8
'''
@描述：上证e互动
@作者：hingbox
@邮箱：hingbox@163.com
@版本：V1.0
@文件名称 : spiders.py
@创建时间：2018/7/23 14:18
'''
import scrapy
from bs4 import BeautifulSoup
from qa.items import QaItem
from qa.items import NewsItem
from qa.dateutils import DateUtils
import datetime
import re
import sys
import json
import time
import uuid
reload(sys)
sys.setdefaultencoding('utf-8')

now_date = DateUtils()

'''
上证e互动 最新提问
'''
class zxtwSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "zxtw"
    def start_requests(self):
        pages = []
        for i in range(1,10):#1,201
            url = 'http://sns.sseinfo.com/ajax/feeds.do?type=10&show=1&pageSize=100&lastid=-1&page='+str(i)
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        div_lists = response.xpath('//div[@class="m_feed_item m_question"]')
        for div_list in div_lists:
            item = QaItem()
            item['nick_name'] = div_list.xpath('./div[@class="m_feed_detail"]/div[@class="m_feed_face"]/a/@title').extract_first()
            item['source'] = 'sh'
            stock = div_list.xpath('./div[@class="m_feed_detail"]/div[@class="m_feed_cnt "]/div[@class="m_feed_txt"]/a/text()').extract_first()
            if stock is not None:
                item['stock'] = stock.replace(':', '').split('(')[0]
                item['code'] = stock.replace(':', '').split('(')[1].replace(')', '')
            else:
                item['stock'] = None
                item['code'] = None
            data = div_list.xpath('./div[@class="m_feed_detail"]/div[@class="m_feed_cnt "]/div[@class="m_feed_txt"]')
            content_str = data.xpath('string(.)').extract_first()
            content = removetnr(str_to_strip(content_str)).replace(':', '')
            item['content'] = content
            item['qa'] = 0
            pub_date = div_list.xpath('./div[@class="m_feed_detail"]/div[@class="m_feed_cnt "]/div[@class="m_feed_func clearfix"]/div[@class="m_feed_from"]/span/text()').extract_first()
            '''
            这个地方需要对时间进行处理
            1.分钟
            2.小时 如果是小时 就用当时时间减去 当前小时数
            3.天
            '''
            if pub_date is not None:
                #匹配是否有前
                tempbefore = pub_date.decode('utf8')
                findwordbefore = u"(前+)"
                patternbefore = re.compile(findwordbefore)
                resultsbefores = patternbefore.findall(tempbefore)
                if len(resultsbefores):#有值
                   # for resultsbefore in resultsbefores:
                   #  if resultsbefore is not None:
                    temp = pub_date.decode('utf8')
                    findwordshours = u"(小时+)"
                    patternhours = re.compile(findwordshours)
                    resulthours = patternhours.findall(temp)
                    if len(resulthours):
                        pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                        item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                        item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                    # else:
                    #      pub_temp = pub_date.replace('月', '-').replace('日', '')
                    #      item['pub_date'] = '2018-'+pub_temp
                else:
                    #昨天
                    tempyestoday = pub_date.decode('utf8')
                    findwordsyestoday = u"(昨天+)"
                    patternyestodays = re.compile(findwordsyestoday)
                    resultyestodays = patternyestodays.findall(tempyestoday)
                    if len(resultyestodays):
                        pub_dates = tempyestoday.replace('昨天 ', '')
                        last_date = (datetime.datetime.now()-datetime.timedelta(days=int(1))).strftime("%Y-%m-%d")
                        item['pub_date'] = last_date+' '+pub_dates
                        # item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(24))).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        pub_temp = pub_date.replace('月', '-').replace('日', '')
                        item['pub_date'] = '2018-'+pub_temp
            else:
                item['pub_date'] = None
            # if pub_date is not None:
            #     #匹配是否有前
            #     temp = pub_date.decode('utf8')
            #     findword = u"(前+)"
            #     pattern = re.compile(findword)
            #     results = pattern.findall(temp)
            #     if len(results):#有值
            #        for result in results:
            #            if result is not None:
            #               temp = pub_date.decode('utf8')
            #               findword=u"(小时+)"
            #               pattern = re.compile(findword)
            #               results = pattern.findall(temp)
            #               for result in results:
            #                   if result is not None:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #                   else:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #            else:
            #              pub_temp = pub_date.replace('月', '-').replace('日', '')
            #              item['pub_date'] = '2018-'+pub_temp
            #     else:
            #         pub_temp = pub_date.replace('月', '-').replace('日', '')
            #         item['pub_date'] = '2018-'+pub_temp
            #
            #
            #     # temp = re.search(r'^(.*)前', pub_date)
            #
            # else:
            #     item['pub_date'] = None

            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, content.decode('utf-8').encode('gbk'))
            #item['uuid'] = None
            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item



'''
上证e互动 最新答复(提问)
'''
class zxdftwSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "zxdftw"
    def start_requests(self):
        pages = []
        for i in range(1,10):#1,450
            #url = 'http://sns.sseinfo.com/ajax/feeds.do?type=11&pageSize=10&lastid=-1&show=1&page='+str(i)
            url = 'http://sns.sseinfo.com/ajax/feeds.do?&type=11&pageSize=100&lastid=-1&show=1&page='+str(i)
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        div_lists = response.xpath('//div[@class="m_feed_item"]')
        for div_list in div_lists:
            item = QaItem()
            item['nick_name'] = div_list.xpath('./div[@class="m_feed_detail m_qa_detail"]/div[@class="m_feed_face"]/a/@title').extract_first()
            item['source'] = 'sh'
            stock = div_list.xpath('./div[@class="m_feed_detail m_qa_detail"]/div[@class="m_feed_cnt "]/div[@class="m_feed_txt"]/a/text()').extract_first()
            if stock is not None:
                item['stock'] = stock.replace(':', '').split('(')[0]
                item['code'] = stock.replace(':', '').split('(')[1].replace(')', '')
            else:
                item['stock'] = None
                item['code'] = None
            data = div_list.xpath('./div[@class="m_feed_detail m_qa_detail"]/div[@class="m_feed_cnt "]/div[@class="m_feed_txt"]')
            content_str = data.xpath('string(.)').extract_first()
            content = removetnr(str_to_strip(content_str)).replace(':', '')
            item['content'] = content
            item['qa'] = 0
            pub_date = div_list.xpath('./div[@class="m_feed_detail m_qa_detail"]/div[@class="m_feed_cnt "]/div[@class="m_feed_func"]/div[@class="m_feed_from"]/span/text()').extract_first()
            '''
            这个地方需要对时间进行处理
            1.分钟 当前时间减去分钟
            2.小时 如果是小时 就用当时时间减去 当前小时数
            3.天 就处理数据格式
            '''
            if pub_date is not None:
                #匹配是否有前
                tempbefore = pub_date.decode('utf8')
                findwordbefore = u"(前+)"
                patternbefore = re.compile(findwordbefore)
                resultsbefores = patternbefore.findall(tempbefore)
                if len(resultsbefores):#有值
                   # for resultsbefore in resultsbefores:
                   #  if resultsbefore is not None:
                    temp = pub_date.decode('utf8')
                    findwordshours = u"(小时+)"
                    patternhours = re.compile(findwordshours)
                    resulthours = patternhours.findall(temp)
                    if len(resulthours):
                        pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                        item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                        item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                    # else:
                    #      pub_temp = pub_date.replace('月', '-').replace('日', '')
                    #      item['pub_date'] = '2018-'+pub_temp
                else:
                    #昨天
                    tempyestoday = pub_date.decode('utf8')
                    findwordsyestoday = u"(昨天+)"
                    patternyestodays = re.compile(findwordsyestoday)
                    resultyestodays = patternyestodays.findall(tempyestoday)
                    if len(resultyestodays):
                        pub_dates = tempyestoday.replace('昨天 ', '')
                        last_date = (datetime.datetime.now()-datetime.timedelta(days=int(1))).strftime("%Y-%m-%d")
                        item['pub_date'] = last_date+' '+pub_dates
                        #item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(24))).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        pub_temp = pub_date.replace('月', '-').replace('日', '')
                        item['pub_date'] = '2018-'+pub_temp
            else:
                item['pub_date'] = None
            # if pub_date is not None:
            #     #匹配是否有前
            #     temp = pub_date.decode('utf8')
            #     findword = u"(前+)"
            #     pattern = re.compile(findword)
            #     results = pattern.findall(temp)
            #     if len(results):#有值
            #        for result in results:
            #            if result is not None:
            #               temp = pub_date.decode('utf8')
            #               findword=u"(小时+)"
            #               pattern = re.compile(findword)
            #               results = pattern.findall(temp)
            #               for result in results:
            #                   if result is not None:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #                   else:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #            else:
            #              pub_temp = pub_date.replace('月', '-').replace('日', '')
            #              item['pub_date'] = '2018-'+pub_temp
            #     else:
            #         pub_temp = pub_date.replace('月', '-').replace('日', '')
            #         item['pub_date'] = '2018-'+pub_temp
            #
            #
            #     # temp = re.search(r'^(.*)前', pub_date)
            #
            # else:
            #     item['pub_date'] = None
            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            #item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, content.decode('utf-8').encode('gbk'))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, content.decode('utf-8').encode('gbk'))
            #item['uuid'] = None
            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item



'''
上证e互动 最新答复(回答)
'''
class zxdfhdSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://sns.sseinfo.com/'
    name = "zxdfhd"
    def start_requests(self):
        pages = []
        for i in range(1,10):#1,201
            url = 'http://sns.sseinfo.com/ajax/feeds.do?&type=11&pageSize=100&lastid=-1&show=1&page='+str(i)
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        div_lists = response.xpath('//div[@class="m_feed_item"]')
        for div_list in div_lists:
            item = QaItem()
            item['nick_name'] = div_list.xpath('./div[@class="m_feed_detail m_qa_detail"]/div[@class="m_feed_face"]/a/@title').extract_first()
            #item['nick_name'] = div_list.xpath('./div[@class="m_feed_detail m_qa"]/div[@class="m_feed_face"]/a/@title').extract_first()
            item['source'] = 'sh'
            #得到股票代码
            stock = div_list.xpath('./div[@class="m_feed_detail m_qa_detail"]/div[@class="m_feed_cnt "]/div[@class="m_feed_txt"]/a/text()').extract_first()
            if stock is not None:
                item['stock'] = stock.replace(':', '').split('(')[0]
                item['code'] = stock.replace(':', '').split('(')[1].replace(')', '')
            else:
                item['stock'] = None
                item['code'] = None
            # stock = div_list.xpath('./div[@class="m_feed_detail m_qa"]/div[@class="m_feed_cnt"]/div[@class="m_feed_txt"]/a/text()').extract_first()
            # if stock is not None:
            #     item['stock'] = stock.replace(':', '').split('(')[0]
            #     item['code'] = stock.replace(':', '').split('(')[1].replace(')', '')
            # else:
            #     item['stock'] = None
            #     item['code'] = None
            data = div_list.xpath('./div[@class="m_feed_detail m_qa"]/div[@class="m_feed_cnt"]/div[@class="m_feed_txt"]')
            content_str = data.xpath('string(.)').extract_first()
            content = removetnr(str_to_strip(content_str))
            item['content'] = content
            item['qa'] = 1
            pub_date = div_list.xpath('./div[@class="m_feed_detail m_qa"]/div[@class="m_feed_func top10"]/div[@class="m_feed_from"]/span/text()').extract_first()
            '''
            这个地方需要对时间进行处理
            1.分钟
            2.小时 如果是小时 就用当时时间减去 当前小时数
            3.天
            '''
            if pub_date is not None:
                #匹配是否有前
                tempbefore = pub_date.decode('utf8')
                findwordbefore = u"(前+)"
                patternbefore = re.compile(findwordbefore)
                resultsbefores = patternbefore.findall(tempbefore)
                if len(resultsbefores):#有值
                   # for resultsbefore in resultsbefores:
                   #  if resultsbefore is not None:
                    temp = pub_date.decode('utf8')
                    findwordshours = u"(小时+)"
                    patternhours = re.compile(findwordshours)
                    resulthours = patternhours.findall(temp)
                    if len(resulthours):
                        pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                        item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                        item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                    # else:
                    #      pub_temp = pub_date.replace('月', '-').replace('日', '')
                    #      item['pub_date'] = '2018-'+pub_temp
                else:
                    #昨天
                    tempyestoday = pub_date.decode('utf8')
                    findwordsyestoday = u"(昨天+)"
                    patternyestodays = re.compile(findwordsyestoday)
                    resultyestodays = patternyestodays.findall(tempyestoday)
                    if len(resultyestodays):
                        pub_dates = tempyestoday.replace('昨天 ', '')
                        last_date = (datetime.datetime.now()-datetime.timedelta(days=int(1))).strftime("%Y-%m-%d")
                        item['pub_date'] = last_date+' '+pub_dates
                        #item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(24))).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        pub_temp = pub_date.replace('月', '-').replace('日', '')
                        item['pub_date'] = '2018-'+pub_temp
            else:
                item['pub_date'] = None
            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, content.decode('utf-8').encode('gbk'))
            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item



def get_date_range(start, end, step=1, format_string="%Y-%m-%d"):
        strptime, strftime = datetime.datetime.strptime, datetime.datetime.strftime
        days = (strptime(end, format_string) - strptime(start, format_string)).days
        return [strftime(strptime(start, format_string) + datetime.timedelta(i), format_string) for i in xrange(0, days, step)]
'''
深交所互动易提问
'''
class sjshdytwSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://irm.cninfo.com.cn/szse/index.html'
    name = "sjshdytw"
    # def start_requests(self):
    #     pages = []
    #     date_list = get_date_range('2018-07-24','2018-07-25',1)
    #     for d in date_list:
    #         for i in range(1,100):#1,201
    #             url = 'http://irm.cninfo.com.cn/ircs/interaction/topSearchForSzse.do?condition.dateFrom='+d+'&condition.dateTo='+d+'&condition.stockcode=&condition.keyWord=&condition.status=-1&condition.searchType=name&condition.questionCla=&condition.questionAtr=&condition.marketType=Z&condition.searchRange=0&condition.questioner=&condition.questionerType=&condition.loginId=&condition.provinceCode=&condition.plate=&pageNo='+str(i)+'&categoryId=&code=&pageSize=10&source=2'
    #             page = scrapy.Request(url)
    #             pages.append(page)
    #     return pages
    #     print ('pages', pages)
    def start_requests(self):
        pages = []
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        for i in range(1,100):#1,201
            url = 'http://irm.cninfo.com.cn/ircs/interaction/topSearchForSzse.do?condition.dateFrom='+current_date+'&condition.dateTo='+current_date+'&condition.stockcode=&condition.keyWord=&condition.status=-1&condition.searchType=name&condition.questionCla=&condition.questionAtr=&condition.marketType=Z&condition.searchRange=0&condition.questioner=&condition.questionerType=&condition.loginId=&condition.provinceCode=&condition.plate=&pageNo='+str(i)+'&categoryId=&code=&pageSize=10&source=2'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        div_lists = response.xpath('//ul[@class="Tl talkList2"]/li')
        for div_list in div_lists:
            item = QaItem()
            nick_name = div_list.xpath('./div[@class="ask_Box clear"]/div[@class="userPic"]/a/span/text()').extract_first()
            item['nick_name'] = strip_remove_tnr(nick_name)
            item['source'] = 'sz'
            stock = div_list.xpath('./div[@class="ask_Box clear"]/div[@class="msg_Box"]/div[@class="msgCnt gray666"]/div/a[@class="blue2"]/text()').extract_first()
            if stock is not None:
                item['stock'] = stock.replace(':', '').split('(')[0]
                item['code'] = stock.replace(':', '').split('(')[1].replace(')', '')
            else:
                item['stock'] = None
                item['code'] = None
            # item['stock'] = None
            # item['code'] = None
            data = div_list.xpath('./div[@class="ask_Box clear"]/div[@class="msg_Box"]/div[@class="msgCnt gray666"]/div/a[@class="cntcolor"]')
            content_str = data.xpath('string(.)').extract_first()
            content = removetnr(str_to_strip(content_str))
            item['content'] = content
            item['qa'] = 0
            pub_date = div_list.xpath('./div[@class="ask_Box clear"]/div[@class="msg_Box"]/div[@class="pubInfo"]/text()').extract_first()
            if pub_date is not None:
                item['pub_date'] = pub_date.replace('年', '-').replace('月', '-').replace('日', '')
            else:
                item['pub_date'] = None
            '''
            这个地方需要对时间进行处理
            1.分钟
            2.小时 如果是小时 就用当时时间减去 当前小时数
            3.天
            '''
            # if pub_date is not None:
            #     #匹配是否有前
            #     temp = pub_date.decode('utf8')
            #     findword = u"(前+)"
            #     pattern = re.compile(findword)
            #     results = pattern.findall(temp)
            #     if len(results):#有值
            #        for result in results:
            #            if result is not None:
            #               temp = pub_date.decode('utf8')
            #               findword=u"(小时+)"
            #               pattern = re.compile(findword)
            #               results = pattern.findall(temp)
            #               for result in results:
            #                   if result is not None:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #                   else:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #            else:
            #              pub_temp = pub_date.replace('月', '-').replace('日', '')
            #              item['pub_date'] = '2018-'+pub_temp
            #     else:
            #         pub_temp = pub_date.replace('月', '-').replace('日', '')
            #         item['pub_date'] = '2018-'+pub_temp
            # else:
            #     item['pub_date'] = None
            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, content.decode('utf-8').encode('gbk'))
            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item



'''
深交所互动易答复(提问)
'''
class sjshdydftwSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "sjshdydftw"
    # def start_requests(self):
    #     pages = []
    #     date_list = get_date_range('2018-01-23','2018-07-23',1)
    #     for d in date_list:
    #         for i in range(1,100):#1,201
    #             url = 'http://irm.cninfo.com.cn/ircs/interaction/lastRepliesForSzse.do?condition.dateFrom='+d+'&condition.dateTo='+d+'&condition.stockcode=&condition.keyWord=&condition.status=-1&condition.searchType=name&condition.questionCla=&condition.questionAtr=&condition.marketType=Z&condition.searchRange=0&condition.questioner=&condition.questionerType=&condition.loginId=&condition.provinceCode=&condition.plate=&pageNo='+str(i)+'&categoryId=&code=&pageSize=10&source=2'
    #             page = scrapy.Request(url)
    #             pages.append(page)
    #     return pages
    #     print ('pages', pages)
    def start_requests(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        pages = []
        for i in range(1,100):#1,201
            url = 'http://irm.cninfo.com.cn/ircs/interaction/lastRepliesForSzse.do?condition.dateFrom='+current_date+'&condition.dateTo='+current_date+'&condition.stockcode=&condition.keyWord=&condition.status=-1&condition.searchType=name&condition.questionCla=&condition.questionAtr=&condition.marketType=Z&condition.searchRange=0&condition.questioner=&condition.questionerType=&condition.loginId=&condition.provinceCode=&condition.plate=&pageNo='+str(i)+'&categoryId=&code=&pageSize=10&source=2'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        div_lists = response.xpath('//div[@class="Tl talkList2"]/div[@class="askBoxOuter clear"]')
        for div_list in div_lists:
            item = QaItem()
            nick_name = div_list.xpath('./div[@class="userPic"]/a/span/text()').extract_first()
            item['nick_name'] = strip_remove_tnr(nick_name)
            item['source'] = 'sz'
            stock = div_list.xpath('./div[@class="msgBox"]/div[@class="msgCnt gray666"]/div/a[@class="blue2"]/text()').extract_first()
            if stock is not None:
                item['stock'] = stock.replace(':', '').split('(')[0]
                item['code'] = stock.replace(':', '').split('(')[1].replace(')', '')
            else:
                item['stock'] = None
                item['code'] = None
            # item['stock'] = None
            # item['code'] = None
            data = div_list.xpath('./div[@class="msgBox"]/div[@class="msgCnt gray666"]/div/a[@class="cntcolor"]')
            content_str = data.xpath('string(.)').extract_first()
            content = removetnr(str_to_strip(content_str))
            item['content'] = content
            item['qa'] = 0
            pub_date = div_list.xpath('./div[@class="msgBox"]/div[@class="pubInfo"]/a/text()').extract_first()
            if pub_date is not None:
                item['pub_date'] = pub_date.replace('年', '-').replace('月', '-').replace('日', '')
            else:
                item['pub_date'] = None
            '''
            这个地方需要对时间进行处理
            1.分钟
            2.小时 如果是小时 就用当时时间减去 当前小时数
            3.天
            '''
            # if pub_date is not None:
            #     #匹配是否有前
            #     temp = pub_date.decode('utf8')
            #     findword = u"(前+)"
            #     pattern = re.compile(findword)
            #     results = pattern.findall(temp)
            #     if len(results):#有值
            #        for result in results:
            #            if result is not None:
            #               temp = pub_date.decode('utf8')
            #               findword=u"(小时+)"
            #               pattern = re.compile(findword)
            #               results = pattern.findall(temp)
            #               for result in results:
            #                   if result is not None:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #                   else:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #            else:
            #              pub_temp = pub_date.replace('月', '-').replace('日', '')
            #              item['pub_date'] = '2018-'+pub_temp
            #     else:
            #         pub_temp = pub_date.replace('月', '-').replace('日', '')
            #         item['pub_date'] = '2018-'+pub_temp
            # else:
            #     item['pub_date'] = None
            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, content.decode('utf-8').encode('gbk'))
            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item


'''
深交所互动易答复(回答)
'''
class sjshdydfhdSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "sjshdydfhd"
    # def start_requests(self):
    #     pages = []
    #     date_list = get_date_range('2018-01-23','2018-07-23',1)
    #     for d in date_list:
    #         for i in range(1,100):#1,100
    #             url = 'http://irm.cninfo.com.cn/ircs/interaction/lastRepliesForSzse.do?condition.dateFrom='+d+'&condition.dateTo='+d+'&condition.stockcode=&condition.keyWord=&condition.status=-1&condition.searchType=name&condition.questionCla=&condition.questionAtr=&condition.marketType=Z&condition.searchRange=0&condition.questioner=&condition.questionerType=&condition.loginId=&condition.provinceCode=&condition.plate=&pageNo='+str(i)+'&categoryId=&code=&pageSize=10&source=2'
    #             page = scrapy.Request(url)
    #             pages.append(page)
    #     return pages
    #     print ('pages', pages)
    def start_requests(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        pages = []
        for i in range(1,100):#1,201
            url = 'http://irm.cninfo.com.cn/ircs/interaction/lastRepliesForSzse.do?condition.dateFrom='+current_date+'&condition.dateTo='+current_date+'&condition.stockcode=&condition.keyWord=&condition.status=-1&condition.searchType=name&condition.questionCla=&condition.questionAtr=&condition.marketType=Z&condition.searchRange=0&condition.questioner=&condition.questionerType=&condition.loginId=&condition.provinceCode=&condition.plate=&pageNo='+str(i)+'&categoryId=&code=&pageSize=10&source=2'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        div_lists = response.xpath('//div[@class="Tl talkList2"]/div[@class="answerBoxOuter clear"]')
        for div_list in div_lists:
            item = QaItem()
            nick_name = div_list.xpath('./div[@class="answerBox"]/div[@class="msgCnt gray666"]/a[@class="blue2"]/text()').extract_first()
            item['nick_name'] = strip_remove_tnr(nick_name)
            item['source'] = 'sz'
            stock = div_list.xpath('./div[@class="userPic"]/span[@class="comName"]/a/text()').extract_first()
            code = div_list.xpath('./div[@class="userPic"]/span[@class="comCode"]/a/text()').extract_first()
            if stock is not None:
                item['stock'] = stock
                item['code'] = code
            else:
                item['stock'] = None
                item['code'] = None
            # item['stock'] = None
            # item['code'] = None
            data = div_list.xpath('./div[@class="answerBox"]/div[@class="msgCnt gray666"]/a[@class="cntcolor"]')
            content_str = data.xpath('string(.)').extract_first()
            content = removetnr(str_to_strip(content_str))
            item['content'] = content
            item['qa'] = 1
            pub_date = div_list.xpath('./div[@class="answerBox"]/div[@class="pubInfo"]/div[@class="pubInfoin"]/p[@class="time_box"]/a/text()').extract_first()
            pub_date = removetnr(pub_date)
            if pub_date is not None:
                item['pub_date'] = pub_date.replace('年', '-').replace('月', '-').replace('日', '')
            else:
                item['pub_date'] = None
            '''
            这个地方需要对时间进行处理
            1.分钟
            2.小时 如果是小时 就用当时时间减去 当前小时数
            3.天
            '''
            # if pub_date is not None:
            #     #匹配是否有前
            #     temp = pub_date.decode('utf8')
            #     findword = u"(前+)"
            #     pattern = re.compile(findword)
            #     results = pattern.findall(temp)
            #     if len(results):#有值
            #        for result in results:
            #            if result is not None:
            #               temp = pub_date.decode('utf8')
            #               findword=u"(小时+)"
            #               pattern = re.compile(findword)
            #               results = pattern.findall(temp)
            #               for result in results:
            #                   if result is not None:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #                   else:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #            else:
            #              pub_temp = pub_date.replace('月', '-').replace('日', '')
            #              item['pub_date'] = '2018-'+pub_temp
            #     else:
            #         pub_temp = pub_date.replace('月', '-').replace('日', '')
            #         item['pub_date'] = '2018-'+pub_temp
            # else:
            #     item['pub_date'] = None
            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, content.decode('utf-8').encode('gbk'))
            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item



'''
demo
'''
class demoSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "demo"
    def start_requests(self):
        pages = []
        for i in range(1,5):#1,201
            url = 'http://irm.cninfo.com.cn/ircs/interaction/lastRepliesForSzse.do?condition.dateFrom=2018-01-23&condition.dateTo=2018-07-23&condition.stockcode=&condition.keyWord=&condition.status=-1&condition.searchType=name&condition.questionCla=&condition.questionAtr=&condition.marketType=Z&condition.searchRange=0&condition.questioner=&condition.questionerType=&condition.loginId=&condition.provinceCode=&condition.plate=&pageNo='+str(i)+'&categoryId=&code=&pageSize=10&source=2'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        div_lists = response.xpath('//div[@class="Tl talkList2"]/div[@class="answerBoxOuter clear"]')
        for div_list in div_lists:
            item = QaItem()
            item['nick_name'] = 'kk'
            item['source'] = 'sz'
            stock = '1'
            code = '2'
            if stock is not None:
                item['stock'] = stock
                item['code'] = code
            else:
                item['stock'] = None
                item['code'] = None
            # item['stock'] = None
            # item['code'] = None
            data = div_list.xpath('./div[@class="answerBox"]/div[@class="msgCnt gray666"]/a[@class="cntcolor"]')
            content_str = data.xpath('string(.)').extract_first()
            content = removetnr(str_to_strip(content_str))
            item['content'] = 'haha'
            item['qa'] = 1
            item['pub_date'] = None
            '''
            这个地方需要对时间进行处理
            1.分钟
            2.小时 如果是小时 就用当时时间减去 当前小时数
            3.天
            '''
            # if pub_date is not None:
            #     #匹配是否有前
            #     temp = pub_date.decode('utf8')
            #     findword = u"(前+)"
            #     pattern = re.compile(findword)
            #     results = pattern.findall(temp)
            #     if len(results):#有值
            #        for result in results:
            #            if result is not None:
            #               temp = pub_date.decode('utf8')
            #               findword=u"(小时+)"
            #               pattern = re.compile(findword)
            #               results = pattern.findall(temp)
            #               for result in results:
            #                   if result is not None:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #                   else:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #            else:
            #              pub_temp = pub_date.replace('月', '-').replace('日', '')
            #              item['pub_date'] = '2018-'+pub_temp
            #     else:
            #         pub_temp = pub_date.replace('月', '-').replace('日', '')
            #         item['pub_date'] = '2018-'+pub_temp
            # else:
            #     item['pub_date'] = None
            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, content.decode('utf-8').encode('gbk'))
            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item










'''
深交所互动易提问 new 2019-04-18版本
'''
class sjhdytwnewSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "sjtwnew"
    def start_requests(self):
        url = 'http://irm.cninfo.com.cn/ircs/index/search'
        # FormRequest 是Scrapy发送POST请求的方法
        for i in range(1,11):
            data = {
                "pageNo": str(i), "pageSize":'100', "searchTypes": '11'
            }
            yield scrapy.FormRequest(
                url=url,
                formdata=data,
                callback=self.parse_page
            )
    '''
    提问
      昵称authorName，内容mainContent，股票名称companyShortName，股票代码stockCode，提问日期pubDate，提问0,
    回答
      昵称authorName，回复内容attachedContent，回复时间 attachedPubDate，股票名称companyShortName，股票代码stockCode,回答1
    '''
    def parse_page(self, response):
        info = json.loads(response.body.strip())
        results = info['results']
        for result in results:
            item = QaItem()
            item['nick_name'] = result['authorName']
            item['source'] = 'sz'

            item['stock'] = result['companyShortName']
            item['code'] = result['stockCode']
            item['content'] = result['mainContent']
            item['qa'] = 0
            pub_date = now_date.timeStamp(int(result['pubDate'].encode("utf-8")))
            item['pub_date'] = pub_date

            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, item['content'].decode('utf-8').encode('gbk'))
            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item






'''
深交所互动易提问 new 2019-04-18版本
'''
class sjhdyhdnewSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "sjhdnew"
    def start_requests(self):
        url = 'http://irm.cninfo.com.cn/ircs/index/search'
        # FormRequest 是Scrapy发送POST请求的方法
        for i in range(1,11):
            data = {
                "pageNo": str(i), "pageSize":'100', "searchTypes": '11'
            }
            yield scrapy.FormRequest(
                url=url,
                formdata=data,
                callback=self.parse_page
            )
    '''
    提问
      昵称authorName，内容mainContent，股票名称companyShortName，股票代码stockCode，提问日期pubDate，提问0,
    回答
      昵称authorName，回复内容attachedContent，回复时间 attachedPubDate，股票名称companyShortName，股票代码stockCode,回答1
    '''
    def parse_page(self, response):
        info = json.loads(response.body.strip())
        results = info['results']
        for result in results:
            item = QaItem()
            item['nick_name'] = result['authorName']
            item['source'] = 'sz'

            item['stock'] = result['companyShortName']
            item['code'] = result['stockCode']
            item['content'] = result['attachedContent']
            item['qa'] = 1
            pub_date = now_date.timeStamp(int(result['attachedPubDate'].encode("utf-8")))
            item['pub_date'] = pub_date

            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, item['content'].decode('utf-8').encode('gbk'))
            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item














#去掉字符串中空格，换行
def removetnr(value):
    if value is not None:
        return value.replace('\r','').replace('\t','').replace('\n','')
    else:
        return None
#将list转换为str
def list_to_str(value):
    if value is not None:
        return "".join(value)
    else:
        return None
#去掉string中空格
def str_to_strip(value):
    if value is not None:
        return value.strip()
    else:
        return None

def strip_remove_tnr(value):
    if value is not None:
        value = value.strip()
        return value.replace('\r', '').replace('\t', '').replace('\n', '').replace(' ', '')
    else:
        return None





