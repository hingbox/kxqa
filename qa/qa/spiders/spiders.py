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
上证e互动
'''
class szhdSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "szhd"
    def start_requests(self):
        pages = []
        for i in range(1,2):#1,201
            url = 'http://sns.sseinfo.com/ajax/feeds.do?type=10&show=1&pageSize=10&lastid=-1&page='+str(i)
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
                findword=u"(前+)"
                pattern = re.compile(findword)
                results = pattern.findall(temp)
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

                # temp = re.search(r'^(.*)前', pub_date)

            else:
                item['pub_date'] = None
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
金投网
'''
class jtwSpiders(scrapy.Spider):
    name = "jtw"
    start_urls = ['https://news.cngold.org/top/list_2411_all.html']
    def parse(self, response):
        li_lists = response.xpath('//div[@class="history_news_content"]/ul/li')
        for li_list in li_lists:
            href = li_list.xpath('./a/@href').extract_first()
            yield scrapy.Request(href,callback=self.parse_list)
            print ('href',href)
    def parse_list(self,response):
        secd_li_lists = response.xpath('//ul[@class="redian_ul shishi_ul"]/li')
        for secd_li_list in secd_li_lists:
            item = NewsItem()
            orgurl = secd_li_list.xpath('./div[@class="fl text"]/a/@href').extract_first()
            item['title'] = secd_li_list.xpath('./div[@class="fl text"]/a/text()').extract_first()
            item['writer'] = secd_li_list.xpath('./div[@class="fl text"]/span[@class="fr ml10"]/text()').extract_first()
            item['orgurl'] = orgurl
            request = scrapy.Request(orgurl, callback=self.parse_detail)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item']
        summary = response.xpath('//div[@class="l_desc"]/text()').extract_first()
        source = response.xpath('//span[@class="l_source"]/text()').extract_first()
        pubdate = response.xpath('//span[@class="l_date"]/text()').extract_first()
        content_str = response.xpath('//div[@class="l_article"]/p/text()').extract()
        if source is not None:
            item['source'] = source
            item['pubdate'] = pubdate
            item['summary'] = summary
            item['content'] = removetnr(str_to_strip(list_to_str(content_str)))
        else:
            item['source'] = response.xpath('//div[@class="article-info"]/span[1]/text()').extract_first()
            item['pubdate'] = response.xpath('//div[@class="article-info"]/span[2]/text()').extract_first()
            item['summary'] = response.xpath('//div[@class="summary"]/p/text()').extract_first()
            content_str = response.xpath('//div[@class="article_con"]/p/text()').extract()
            item['content'] = removetnr(str_to_strip(list_to_str(content_str)))
        item['sourcecategory'] = '新闻热点'
        item['source_from'] = '金投网'
        item['type'] = None
        item['create_date']=now_date.get_now_time()
        item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS,response.url)
        yield item





'''
发展论坛
'''
class fzltSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://forum.home.news.cn'
    name = "fzlt"
    def start_requests(self):
        pages = []
        # for i in range(1,56257):#1,56257
        #     url = 'http://forum.home.news.cn/list/50-0-0-'+str(i)+'.html'
        #     page = scrapy.Request(url)
        #     pages.append(page)
        for page in range(1,10398):#1,10398
            url = 'http://forum.home.news.cn/list/98-0-0-'+str(page)+'.html'
            page = scrapy.Request(url)
            pages.append(page)
        for i in range(1,10511):#1,10511
            url = 'http://forum.home.news.cn/list/75-0-0-'+str(i)+'.html'
            page = scrapy.Request(url)
            pages.append(page)
        for i in range(1,860):#1,4023
            url = 'http://forum.home.news.cn/list/50-224-0-'+str(i)+'.html'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages',pages)
    def parse(self, response):
        dl_lists = response.xpath('//div[@id="lt-item"]/dl[@class="item"]')
        for dl_list in dl_lists:
            item = NewsItem()
            orgurl = dl_list.xpath('./dt/a[@class="bt"]/@href').extract_first()
            item['type'] = dl_list.xpath('./dt/span[@class="bq rt"]/text()').extract_first()
            item['title'] = dl_list.xpath('./dt/a[@class="bt"]/text()').extract_first()
            orgurl = self.static_url + orgurl
            item['orgurl']=orgurl
            request = scrapy.Request(orgurl,callback=self.parse_item)
            request.meta['item'] = item
            yield request
    def parse_item(self,response):
        item = response.meta['item']
        data = response.xpath('//div[@id="message_"]')
        content_str = data.xpath('string(.)').extract_first()
        item['content'] = removetnr(str_to_strip(content_str))
        #content_str = response.xpath('//div[@id="message_"]/p/span/text()').extract()
        item['pubdate'] = response.xpath('//ul[@class="de-xx clear"]/li[@class="fr"]/span/text()').extract_first()
        #选取div标签中最后一个p标签
        datas = response.xpath('//div[@id="message_"]/p[last()]')
        source_str = datas.xpath('string(.)').extract_first()
        if source_str is not None:
            if len(removetnr(str_to_strip(source_str))) > 40:
                item['source'] = None
            else:
                item['source'] = removetnr(str_to_strip(source_str))
        else:
            item['source'] = None
        item['source_from']='发展论坛'
        item['sourcecategory']= None
        item['summary']=None
        #item['type']=None
        item['writer']=None
        item['create_date']=now_date.get_now_time()

        item['uuid']=uuid.uuid5(uuid.NAMESPACE_DNS,response.url)
        yield item
       # print ('content',content,'pubdate',pubdate,'source',source)










'''
解放日报
'''
class jfrbSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://www.jfdaily.com'
    name = "jfrb"
    def start_requests(self):
        pages = []
        for i in range(1,730):#1,730
            url = 'http://www.jfdaily.com/news/list?section=2&page='+str(page)
            page = scrapy.Request(url)
            pages.append(page)
        # for i in range(1,486):#1,486
        #     url = 'http://hao.c029.com/list-3-'+str(i)+'.html'
        #     page = scrapy.Request(url)
        #     pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        dl_lists = response.xpath('//div[@class="chengshi"]/div[@class="chengshi_wz"]')
        for dl_list in dl_lists:
            item = NewsItem()
            orgurl = dl_list.xpath('./div[@class="chengshi_wz_h"]/a/@href').extract_first()
            item['title'] = dl_list.xpath('./div[@class="chengshi_wz_h"]/a/text()').extract_first()
            item['summary'] = dl_list.xpath('./div[@class="chengshi_wz_m"]/text()').extract_first()
            pubdate_str = dl_list.xpath('./div[@class="chengshi_wz_f"]/text()').extract_first()
            item['pubdate'] = str_to_strip(pubdate_str)[-19:]
            orgurl = self.static_url + orgurl
            item['orgurl'] = orgurl
            request = scrapy.Request(orgurl, callback=self.parse_item)
            request.meta['item'] = item
            yield request

    def parse_item(self,response):
        item = response.meta['item']
        data = response.xpath('//div[@id="newscontents"]')
        content_str = data.xpath('string(.)').extract_first()
        item['content'] = removetnr(str_to_strip(content_str))
        source_str = response.xpath('//div[@class="fenxiang_zz"]/span[1]/text()').extract_first()
        writer_str = response.xpath('//div[@class="fenxiang_zz"]/span[2]/text()').extract_first()
        item['source'] = str_to_strip(source_str)
        item['sourcecategory'] = '财经'
        item['source_from'] = '解放日报'
        item['type'] = None
        item['writer'] = writer_str
        item['create_date'] = now_date.get_now_time()
        item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, response.url)
        yield item





'''
东方网
'''
class dfwSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://www.jfdaily.com'
    name = "dfw"
    def start_requests(self):
        pages = []
        for i in range(0,7):#1
            if i == 0:
                url = 'http://news.eastday.com/gd2008/news/index.html'
            else:
                url = 'http://news.eastday.com/gd2008/news/index'+str(i)+'.html'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        dl_lists = response.xpath('//div[@class="leftsection"]/ul/li')
        for dl_list in dl_lists:
            item = NewsItem()
            orgurl = dl_list.xpath('./a[2]/@href').extract_first()
            item['title'] = dl_list.xpath('./a[2]/text()').extract_first()
            item['sourcecategory'] = dl_list.xpath('./a[1]/text()').extract_first()
            item['pubdate'] = dl_list.xpath('./span/text()').extract_first()
            #print ('orgurl',orgurl,'title',title,'sourcecategory',sourcecategory,'pubdate',pubdate)
            item['orgurl'] = orgurl
            request = scrapy.Request(orgurl, callback=self.parse_item)
            request.meta['item'] = item
            yield request
    def parse_item(self,response):
        item = response.meta['item']
        data = response.xpath('//div[@id="zw"]')
        content_str = data.xpath('string(.)').extract_first()
        item['content'] = removetnr(str_to_strip(content_str))
        source_str = response.xpath('//div[@class="time grey12a fc lh22"]/p[2]/a/text()').extract_first()
        item['source'] = str_to_strip(source_str)
        #item['sourcecategory'] = '财经'
        item['source_from'] = '东方网'
        item['type'] = None
        item['writer'] = None
        item['summary'] = None
        item['create_date'] = now_date.get_now_time()
        item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, response.url)
        yield item


'''
天山网
'''
class tswSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://www.jfdaily.com'
    name = "tsw"
    # def start_requests(self):
    #     pages = []
    #     for i in range(0,7):#1
    #         if i == 0:
    #             url = 'http://news.eastday.com/gd2008/news/index.html'
    #         else:
    #             url = 'http://news.eastday.com/gd2008/news/index'+str(i)+'.html'
    #         page = scrapy.Request(url)
    #         pages.append(page)
    #     return pages
    #     print ('pages', pages)
    start_urls = ['http://news.ts.cn/sz/index.shtml','http://news.ts.cn/gn/index.shtml','http://news.ts.cn/gj/index.shtml']
    #custom_settings = {'COOKIES_ENABLED':True}
    def parse(self, response):
        dl_lists = response.xpath('//ul[@class="tabslist1"]/li')
        for dl_list in dl_lists:
            item = NewsItem()
            extra = {'temp_url':response.url}
            orgurl = dl_list.xpath('./a/@href').extract_first()
            item['title'] = dl_list.xpath('./a/text()').extract_first()
            #item['sourcecategory'] = dl_list.xpath('./a[1]/text()').extract_first()
            #item['pubdate'] = dl_list.xpath('./span/text()').extract_first()
            #print ('orgurl',orgurl,'title',item['title'])
            item['orgurl'] = orgurl
            request = scrapy.Request(orgurl, callback=self.parse_item)
            request.meta['item'] = item
            request.meta['extra'] = extra
            yield request
    def parse_item(self,response):
        item = response.meta['item']
        extra = response.meta['extra']
        data = response.xpath('//div[@class="hy-active"]')
        content_str = data.xpath('string(.)').extract_first()
        item['content'] = removetnr(str_to_strip(content_str))
        source_str = response.xpath('//p[@class="active-info2"]/text()').extract_first()
        source_temp = removetnr(str_to_strip(source_str))
        if re.search(u'年',source_temp):
            item['pubdate'] = source_temp[0:16].replace("年",'-').replace('月','-').replace('日','')
            source = source_temp.split('来源：')
            item['source'] = source[1]
        else:
            source = source_temp.split('来源：')
            item['source'] = source[1]
            item['pubdate']= None
        #item['source'] = source_str_temp.encode('unicode-escape').decode('string_escape')
        temp_url = extra['temp_url']
        if re.search('sz', temp_url):
            item['sourcecategory'] = '时政要闻'
        elif re.search('gn',temp_url):
            item['sourcecategory'] = '国内新闻'
        else:
            item['sourcecategory'] = '国际新闻'
        item['source_from'] = '天山网'
        item['type'] = None
        item['writer'] = None
        item['summary'] = None
        #item['pubdate']= None
        item['create_date'] = now_date.get_now_time()
        item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, response.url)
        yield item

'''
中国青年网
'''
class zgqnwSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "zgqnw"

    def start_requests(self):
        pages = []
        for i in range(0,17):#1
            if i == 0:
                url = 'http://finance.youth.cn/finance_yw/'
            else:
                url = 'http://finance.youth.cn/finance_yw/index_'+str(i)+'.htm'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        dl_lists = response.xpath('//div[@class="rdwz"]/ul/li')
        for dl_list in dl_lists:
            item = NewsItem()
            item['pubdate'] = dl_list.xpath('./font/text()').extract_first()
            item['title'] = dl_list.xpath('./a/text()').extract_first()
            orgurl = dl_list.xpath('./a/@href').extract_first()
            s = re.search("../(.*)",orgurl)
            if s:
                s = s.group(1)
                # print ('pubdate',pubdate,'title',title,'orgurl',static_url+s)
                item['orgurl'] = self.static_url+s
                request = scrapy.Request(self.static_url+s, callback=self.parse_item)
                request.meta['item'] = item
                yield request
    def parse_item(self,response):
        item = response.meta['item']
        data = response.xpath('//div[@class="TRS_Editor"]')
        content_str = data.xpath('string(.)').extract_first()
        item['content'] = removetnr(str_to_strip(content_str))
        source_str = response.xpath('//div[@class="time grey12a fc lh22"]/p[2]/a/text()').extract_first()
        # item['source'] = str_to_strip(source_str)
        item['source'] = None
        item['sourcecategory'] = '财经'
        item['source_from'] = '中国青年网'
        item['type'] = None
        item['writer'] = None
        item['summary'] = None
        item['create_date'] = now_date.get_now_time()
        item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, response.url)
        yield item



'''
中国质量协会
'''
class zgzlxhSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "zgzlxh"

    def start_requests(self):
        pages = []
        for i in range(1,53):
            if i == 1:
                url = 'http://www.caq.org.cn/html/xhxw/list.html'
            else:
                url = 'http://www.caq.org.cn/html/xhxw/list_'+str(i)+'.html'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        dl_lists = response.xpath('//div[@class="listBox Box"]/ul/li')
        for dl_list in dl_lists:
            item = NewsItem()
            pubdate = dl_list.xpath('./span/text()').extract_first()
            item['pubdate'] = pubdate.replace('/', '-')
            item['title'] = dl_list.xpath('./a/@title').extract_first()
            orgurl = dl_list.xpath('./a/@href').extract_first()
            item['orgurl'] = orgurl
            # s = re.search("../(.*)",orgurl)
            # if s:
            #     s = s.group(1)
            #     # print ('pubdate',pubdate,'title',title,'orgurl',static_url+s)
            #     item['orgurl'] = self.static_url+s
            request = scrapy.Request(orgurl, callback=self.parse_item)
            request.meta['item'] = item
            yield request
    def parse_item(self,response):
        item = response.meta['item']
        data = response.xpath('//div[@class="showBox"]')
        content_str = data.xpath('string(.)').extract_first()
        item['content'] = removetnr(str_to_strip(content_str))
        source_str = response.xpath('//div[@class="time grey12a fc lh22"]/p[2]/a/text()').extract_first()
        # item['source'] = str_to_strip(source_str)
        item['source'] = None
        item['sourcecategory'] = '新闻'
        item['source_from'] = '中国质量协会'
        item['type'] = None
        item['writer'] = None
        item['summary'] = None
        item['create_date'] = now_date.get_now_time()
        item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, response.url)
        yield item



'''
安青网
'''
class aqwSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "aqw"


'''
云南网
'''
class ynwSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "ynw"
    def start_requests(self):
        pages = []
        for i in range(2,201):#1,201
            if i == 1:
                url ='http://www.yunnan.cn/node_14184.htm'
            else:
                url = 'http://www.yunnan.cn/node_14184_'+str(i)+'.htm'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        dl_lists = response.xpath('//div[@class="xx ohd clear"]/div[@class="xlayer02 yh ohd clear"]')
        for dl_list in dl_lists:
            item = NewsItem()
            pubdate = dl_list.xpath('./span[@class="fs3"]/text()').extract_first()
            item['pubdate'] = pubdate.replace('(', '').replace(')', '')
            item['title'] = dl_list.xpath('./span[@class="fs1"]/a/text()').extract_first()
            orgurl = dl_list.xpath('./span[@class="fs1"]/a/@href').extract_first()
            print('[orgurl]',orgurl)
            item['summary'] = None
            item['orgurl'] = orgurl
            # item['sourcecategory'] = get_url_by_name.get_type_from_url(response.url)
            # s = re.search("../(.*)",orgurl)
            # if s:
            #     s = s.group(1)
            #     # print ('pubdate',pubdate,'title',title,'orgurl',static_url+s)
            #     item['orgurl'] = self.static_url+s
            request = scrapy.Request(orgurl, callback=self.parse_item)
            request.meta['item'] = item
            yield request
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
同花顺金融服务网
'''
class thsjrwSpiders(scrapy.Spider):
    def __init__(self):
        self.static_url = 'http://finance.youth.cn/'
    name = "thsjrw"
    def start_requests(self):
        pages = []
        for i in range(1,50):#1,150
            if i == 1:
                url ='http://stock.10jqka.com.cn/jiepan_list/getsoft/'
            else:
                url = 'http://stock.10jqka.com.cn/jiepan_list/getsoft/index_'+str(i)+'.shtml'
            page = scrapy.Request(url)
            pages.append(page)
        return pages
        print ('pages', pages)

    def parse(self, response):
        dl_lists = response.xpath('//div[@id="artlist"]/ul')
        for dl_list in dl_lists:
            li_lists = dl_list.xpath('./li')
            for li_list in li_lists:
                item = NewsItem()
                pubdate = li_list.xpath('./em/text()').extract_first()
                item['pubdate'] = pubdate.replace('(', '').replace(')', '')
                item['title'] = li_list.xpath('./a/@title').extract_first()
                orgurl = li_list.xpath('./a/@href').extract_first()
                print('[orgurl]',orgurl)
                item['summary'] = None
                item['orgurl'] = orgurl
                # item['sourcecategory'] = get_url_by_name.get_type_from_url(response.url)
                # s = re.search("../(.*)",orgurl)
                # if s:
                #     s = s.group(1)
                #     # print ('pubdate',pubdate,'title',title,'orgurl',static_url+s)
                #     item['orgurl'] = self.static_url+s
                request = scrapy.Request(orgurl, callback=self.parse_item)
                request.meta['item'] = item
                yield request
    def parse_item(self,response):
        item = response.meta['item']
        data = response.xpath('//div[@class="main-text atc-content"]')
        content_str = data.xpath('string(.)').extract_first()
        item['content'] = removetnr(str_to_strip(content_str))
        source_str = response.xpath('//span[@class="xt2 yh fl"]/text()').extract_first()
        # item['source'] = str_to_strip(source_str)
        item['source'] = removetnr(str_to_strip(response.xpath('//span[@id="source_baidu"]/text()').extract_first()))
        item['sourcecategory'] = '金融'
        item['source_from'] = '同花顺金融服务网'
        item['type'] = None
        item['writer'] = None
        # item['summary'] = None
        item['create_date'] = now_date.get_now_time()
        item['uuid'] = uuid.uuid5(uuid.NAMESPACE_DNS, response.url)
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





