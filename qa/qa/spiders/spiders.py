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
        for i in range(1,2):#1,201
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
                temp = pub_date.decode('utf8')
                findword = u"(前+)"
                pattern = re.compile(findword)
                results = pattern.findall(temp)
                if len(results):#有值
                   for result in results:
                       if result is not None:
                          temp = pub_date.decode('utf8')
                          findword=u"(小时+)"
                          pattern = re.compile(findword)
                          results = pattern.findall(temp)
                          for result in results:
                              if result is not None:
                                pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                                item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                              else:
                                pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                                item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                       else:
                         pub_temp = pub_date.replace('月', '-').replace('日', '')
                         item['pub_date'] = '2018-'+pub_temp
                else:
                    pub_temp = pub_date.replace('月', '-').replace('日', '')
                    item['pub_date'] = '2018-'+pub_temp


                # temp = re.search(r'^(.*)前', pub_date)

            else:
                item['pub_date'] = None
            # if pub_date is not None:
            #     #匹配是否有前
            #
            #     temp = pub_date.decode('utf8')
            #     findword=u"(前+)"
            #     pattern = re.compile(findword)
            #     results = pattern.findall(temp)
            #     for result in results:
            #         if result is not None:
            #             temp = pub_date.decode('utf8')
            #             findword=u"(小时+)"
            #             pattern = re.compile(findword)
            #             results = pattern.findall(temp)
            #             for result in results:
            #                 if result is not None:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #                 else:
            #                     pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
            #                     item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
            #         else:
            #             pub_temp = pub_date.replace('月', '-').replace('日', '')
            #             item['pub_date'] = '2018-'+pub_temp
            #
            #     # temp = re.search(r'^(.*)前', pub_date)
            #
            # else:
            #     item['pub_date'] = None
            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, content.decode('utf-8').encode('gbk'))

            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item
            # # item['sourcecategory'] = get_url_by_name.get_type_from_url(response.url)
            # # s = re.search("../(.*)",orgurl)
            # # if s:
            # #     s = s.group(1)
            # #     # print ('pubdate',pubdate,'title',title,'orgurl',static_url+s)
            # #     item['orgurl'] = self.static_url+s
            # request = scrapy.Request(orgurl, callback=self.parse_item)
            # request.meta['item'] = item
            # yield request
    def parse_item(self,response):
        item = response.meta['item']
        data = response.xpath('//div[@id="layer216"]')
        content_str = data.xpath('string(.)').extract_first()
        item['content'] = removetnr(str_to_strip(content_str))
        source_str = response.xpath('//span[@class="xt2 yh fl"]/text()').extract_first()
        # item['source'] = str_to_strip(source_str)
        item['source'] = removetnr(str_to_strip(response.xpath('//span[@class="xt2 yh fl"]/text()').extract_first()))
        item['sourcecategory'] = '云南要闻'
        item['source_from'] = '云南网'
        item['type'] = None
        item['writer'] = removetnr(str_to_strip(response.xpath('//div[@class="fr"]/text()').extract_first()))
        # item['summary'] = None
        item['create_date'] = now_date.get_now_time()
        item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, response.url)
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
        for i in range(1,2):#1,201
            #url = 'http://sns.sseinfo.com/ajax/feeds.do?type=11&pageSize=10&lastid=-1&show=1&page='+str(i)
            url = 'http://sns.sseinfo.com/ajax/feeds.do?&type=11&pageSize=10&lastid=-1&show=1&page='+str(i)
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
            1.分钟
            2.小时 如果是小时 就用当时时间减去 当前小时数
            3.天
            '''
            if pub_date is not None:
                #匹配是否有前
                temp = pub_date.decode('utf8')
                findword = u"(前+)"
                pattern = re.compile(findword)
                results = pattern.findall(temp)
                if len(results):#有值
                   for result in results:
                       if result is not None:
                          temp = pub_date.decode('utf8')
                          findword=u"(小时+)"
                          pattern = re.compile(findword)
                          results = pattern.findall(temp)
                          for result in results:
                              if result is not None:
                                pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                                item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                              else:
                                pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                                item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                       else:
                         pub_temp = pub_date.replace('月', '-').replace('日', '')
                         item['pub_date'] = '2018-'+pub_temp
                else:
                    pub_temp = pub_date.replace('月', '-').replace('日', '')
                    item['pub_date'] = '2018-'+pub_temp


                # temp = re.search(r'^(.*)前', pub_date)

            else:
                item['pub_date'] = None
            item['create_date'] = now_date.get_now_time()
            #print ('===',type(content))
            item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, content.decode('utf-8').encode('gbk'))
            #print('nick_name',nick_name,'stock',stock,'code',code,'content',content,'pub_date',pub_date)
            yield item





'''
上证e互动 最新答复(回答)
'''
class zxdfhdSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "zxdfhd"
    def start_requests(self):
        pages = []
        for i in range(1,2):#1,201
            url =  url = 'http://sns.sseinfo.com/ajax/feeds.do?&type=11&pageSize=10&lastid=-1&show=1&page='+str(i)
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        div_lists = response.xpath('//div[@class="m_feed_item"]')
        for div_list in div_lists:
            item = QaItem()
            item['nick_name'] = div_list.xpath('./div[@class="m_feed_detail m_qa"]/div[@class="m_feed_face"]/a/@title').extract_first()
            item['source'] = 'sh'
            # stock = div_list.xpath('./div[@class="m_feed_detail m_qa"]/div[@class="m_feed_cnt"]/div[@class="m_feed_txt"]/a/text()').extract_first()
            # if stock is not None:
            #     item['stock'] = stock.replace(':', '').split('(')[0]
            #     item['code'] = stock.replace(':', '').split('(')[1].replace(')', '')
            # else:
            #     item['stock'] = None
            #     item['code'] = None
            item['stock'] = None
            item['code'] = None
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
                temp = pub_date.decode('utf8')
                findword = u"(前+)"
                pattern = re.compile(findword)
                results = pattern.findall(temp)
                if len(results):#有值
                   for result in results:
                       if result is not None:
                          temp = pub_date.decode('utf8')
                          findword=u"(小时+)"
                          pattern = re.compile(findword)
                          results = pattern.findall(temp)
                          for result in results:
                              if result is not None:
                                pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                                item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(hours=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                              else:
                                pub_date = re.findall(r"\d+\.?\d*", pub_date)[0]
                                item['pub_date'] = (datetime.datetime.now()-datetime.timedelta(minutes=int(pub_date))).strftime("%Y-%m-%d %H:%M:%S")
                       else:
                         pub_temp = pub_date.replace('月', '-').replace('日', '')
                         item['pub_date'] = '2018-'+pub_temp
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




'''
深交所互动易提问
'''
class sjshdytwSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "sjshdytw"
    def start_requests(self):
        pages = []
        for i in range(1,5):#1,201
            url = 'http://irm.cninfo.com.cn/ircs/interaction/topSearchForSzse.do?condition.dateFrom=2018-01-23&condition.dateTo=2018-07-23&condition.stockcode=&condition.keyWord=&condition.status=-1&condition.searchType=name&condition.questionCla=&condition.questionAtr=&condition.marketType=Z&condition.searchRange=0&condition.questioner=&condition.questionerType=&condition.loginId=&condition.provinceCode=&condition.plate=&pageNo='+str(i)+'&categoryId=&code=&pageSize=10&source=2'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        div_lists = response.xpath('//ul[@class="Tl talkList2"]/li')
        for div_list in div_lists:
            item = QaItem()
            item['nick_name'] = div_list.xpath('./div[@class="ask_Box clear"]/div[@class="userPic"]/a/span/text()').extract_first()
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
    def start_requests(self):
        pages = []
        for i in range(1,5):#1,201
            url = 'http://irm.cninfo.com.cn/ircs/interaction/lastRepliesForSzse.do?condition.dateFrom=2018-01-23&condition.dateTo=2018-07-23&condition.stockcode=&condition.keyWord=&condition.status=-1&condition.searchType=name&condition.questionCla=&condition.questionAtr=&condition.marketType=Z&condition.searchRange=0&condition.questioner=&condition.questionerType=&condition.loginId=&condition.provinceCode=&condition.plate=&pageNo='+str(i)+'&categoryId=&code=&pageSize=10&source=2'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        div_lists = response.xpath('//div[@class="Tl talkList2"]/div[@class="askBoxOuter clear"]')
        for div_list in div_lists:
            item = QaItem()
            item['nick_name'] = div_list.xpath('./div[@class="userPic"]/a/span/text()').extract_first()
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
            pub_date = div_list.xpath('./div[@class="msgBox"]/div[@class="pubInfo"]/text()').extract_first()
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
            item['nick_name'] = div_list.xpath('./div[@class="userPic"]/span[@class="comName"]/a/text()').extract_first()
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
        return value.replace('\r','').replace('\t','').replace('\n','')
    else:
        return None





