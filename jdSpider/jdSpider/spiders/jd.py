# -*- coding: utf-8 -*-
import scrapy
from jdSpider.items import JdspiderItem
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
import time
import random

class JdSpider(scrapy.Spider):
    name = 'jd'
    start_urls = []
    allow_domain = ["item.jd.com"]

    def __init__(self):
        self.base_url = "https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&psort=3&page={}&s=361&click=0"
        self.start_urls.append(self.base_url.format(21))
        self.page = 10
        self.browser = webdriver.Edge()

    def parse(self, response):
        url = response.url
        self.browser.get(url)
        time.sleep(random.random()*1)
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(random.random()*2)
        response = HtmlResponse(url=self.browser.current_url,body=self.browser.page_source,encoding='utf-8',request=response)
        if  self.page > 20: #爬取10页数据
            return
        hrefs = response.xpath('//div[@class="gl-i-wrap"]/div[@class="p-img"]/a/@href').extract()
        itemn = len(hrefs)
        for i in range(itemn): #解析商品详情页
            url = "https:" + hrefs[i]
            self.browser.get(url)
            time.sleep(random.random()*1)
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.random()*2)
            response = HtmlResponse(url=self.browser.current_url,body=self.browser.page_source,encoding='utf-8',request=response)
            item = JdspiderItem()
            store = response.xpath('//div[@class="name"]/a[1]/text()').extract() #店铺
            if not store:
                store = [""]
            sale = response.xpath('//div[@id="comment-count"]/a[1]/text()').extract() #销量（以评价数记）
            if not sale:
                sale = [""]
            model = response.xpath('//ul[@class="parameter2 p-parameter-list"]/li[1]/text()').extract() #型号
            if not model:
                model = [""]
            item['versions'] = {}
            try: #寻找可选版本
                wait = WebDriverWait(self.browser,10).until(
                    lambda x: x.find_element_by_xpath('//div[@data-type="版本"]/div[@class="dd"]/div')
                )
                response = HtmlResponse(url=self.browser.current_url,body=self.browser.page_source,encoding='utf-8',request=response)
                versions = response.xpath('//div[@data-type="版本"]/div[@class="dd"]/div/@data-value').extract() #可选版本
                for version in versions: #获取版本-价格
                    try:
                        v = WebDriverWait(self.browser,10).until(
                            lambda x: x.find_element_by_xpath('//a[@clstag="shangpin|keycount|product|yanse-%s"]'%(version))
                        )
                        self.browser.execute_script("arguments[0].click();",v)
                    except TimeoutException as te:
                        item['versions'][""] = ""
                    try: #等待价格加载
                        time.sleep(4)
                        wait = WebDriverWait(self.browser,10).until(
                            lambda x: x.find_element_by_xpath('//div[@class="summary-price J-summary-price"]//*[contains(text(),".")]')
                        )
                        response = HtmlResponse(url=self.browser.current_url,body=self.browser.page_source,encoding='utf-8',request=response)
                        price = response.xpath('//span[@class="p-price"]/span[2]/text()').extract() #价格（直售）
                        if not price:
                            price = response.xpath('//span[@class="p-price ys-price"]/span[2]/text()').extract() #价格（预售）
                        if not price:
                            price = [""]
                        item['versions'][version] = price[0]
                    except TimeoutException as te:
                        item['versions'][""] = ""
            except TimeoutException as te:
                try: #版本唯一，寻找价格
                    wait = WebDriverWait(self.browser,10).until(
                        lambda x: x.find_element_by_xpath('//div[@class="summary-price J-summary-price"]//*[contains(text(),".")]')
                    )
                    response = HtmlResponse(url=self.browser.current_url,body=self.browser.page_source,encoding='utf-8',request=response)
                    price = response.xpath('//span[@class="p-price"]/span[2]/text()').extract() #价格（直售）
                    if not price:
                        price = response.xpath('//span[@class="p-price ys-price"]/span[2]/text()').extract() #价格（预售）
                    if not price:
                        price = [""]
                    item['versions'][""] = price[0]
                except TimeoutException as te:
                    item['versions'][""] = ""
            finally:
                item['store'] = store[0]
                item['sale'] = sale[0]
                item['model'] = model[0].replace("商品名称：","")
                item['i'] = i+1
                item['page'] = self.page
                item['ptotal'] = itemn
                print(f'{item["i"]} / {item["page"]} 共{item["ptotal"]}')
                yield item
        self.page = self.page + 1
        yield scrapy.Request(url=self.base_url.format(2*self.page+1),callback=self.parse)
