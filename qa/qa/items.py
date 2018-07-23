# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    uuid = scrapy.Field()#uuid
    nick_name = scrapy.Field()#标题
    pub_date = scrapy.Field()#来源
    content = scrapy.Field()#原始url
    source = scrapy.Field()#类型
    stock = scrapy.Field()#内容
    code = scrapy.Field()#作者
    qa = scrapy.Field()#摘要
    create_date = scrapy.Field()#创建时间

class NewsItem(scrapy.Item):
    pass
