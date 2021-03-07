# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JdspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    model = scrapy.Field() #型号
    store = scrapy.Field() #店铺
    sale = scrapy.Field() #销量
    versions = scrapy.Field() #版本-价格
    page = scrapy.Field() #商品所属页号
    i = scrapy.Field() #商品在页中所属序号
    ptotal = scrapy.Field() #商品所在页总商品数
