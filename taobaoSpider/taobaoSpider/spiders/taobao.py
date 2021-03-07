import scrapy
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import time
import random
import re

from taobaoSpider.items import TaobaospiderItem

def login(browser, username, password):
    time.sleep(random.random() * 2)
    browser.execute_script("Object.defineProperties(navigator,{webdriver:{get:() => false}})")
    #选择密码登录
    try:
        browser.find_element_by_xpath('//*[@class="forget-pwd J_Quick2Static"]').click()
    except Exception as e:
        pass
    browser.find_element_by_id('TPL_username_1').clear()
    browser.find_element_by_id('TPL_username_1').send_keys(username) #模拟输入用户名
    time.sleep(random.random() * 2)
    #可能会多次滑动验证
    while True:
        browser.find_element_by_id('TPL_password_1').send_keys(password) #模拟输入密码
        time.sleep(random.random() * 2)
        try:
            butt = browser.find_element_by_id('nc_1_n1z')
            action = webdriver.ActionChains(browser)
            action.click_and_hold(butt).perform()
            action.reset_actions()
            action.move_by_offset(300, 0).perform()
            time.sleep(random.random() * 2)
        except:
            pass
        button = browser.find_element_by_id('J_SubmitStatic')
        button.click()  #模拟登录
        time.sleep(random.random() * 2)
        cookies = browser.get_cookies() #获取cookies信息
        if len(cookies) > 10:
            break
    return cookies

def get_element(webelement, xpath):
    try:
        element = webelement.find_element_by_xpath(xpath)
        return element
    except:
        return None

def select_opt(browser):
    #网络类型任选（此处选第一个可选项）
    try:
        v = browser.find_element_by_xpath('//ul[@data-property="网络类型"]/li[not(contains(@class,"stock"))][1]')
        if 'selected' not in v.get_attribute('class'):
            browser.execute_script("arguments[0].click();",v.find_element_by_tag_name('a'))
    except:
        pass
    #机身颜色任选，同上
    try:
        v = browser.find_element_by_xpath('//ul[@data-property="机身颜色"]/li[not(contains(@class,"stock"))][1]')
        if 'selected' not in v.get_attribute('class'):
            browser.execute_script("arguments[0].click();",v.find_element_by_tag_name('a'))
    except:
        pass
    #套餐类型可选，同上
    try:
        v = browser.find_element_by_xpath('//ul[@data-property="套餐类型"]/li[not(contains(@class,"stock"))][1]')
        if 'selected' not in v.get_attribute('class'):
            browser.execute_script("arguments[0].click();",v.find_element_by_tag_name('a'))
    except:
        pass
    #版本类型可选，同上
    try:
        v = browser.find_element_by_xpath('//ul[@data-property="版本类型"]/li[not(contains(@class,"stock"))][1]')
        if 'selected' not in v.get_attribute('class'):
            browser.execute_script("arguments[0].click();",v.find_element_by_tag_name('a'))
    except:
        pass

class TaobaoSpider(scrapy.Spider):
    name = 'taobao'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = input("tb_username: ")
        self.password = input("tb_password: ")
        self.browser = webdriver.Edge()
        self.browser.get('https://login.taobao.com/member/login.html')
        self.browser.delete_all_cookies()
        self.cookies = login(self.browser,self.username,self.password)
        time.sleep(random.random()*4)
        self.page = 15
        self.base_url = "https://s.taobao.com/search?spm=a1z02.1.6856637.d4910789&area=c2c&sourceId=tb.index&search_type=mall&ssid=s5-e&commend=all&q=%E6%89%8B%E6%9C%BA&suggest=0_2&_input_charset=utf-8&wq=shouji&suggest_query=shouji&source=suggest&sort=sale-desc&bcoffset=0&p4ppushleft=%2C44&s={}"

    def start_requests(self):
        yield scrapy.Request(url=self.base_url.format((self.page-1)*44),callback=self.parse,cookies=self.cookies)

    def parse(self, response):
        if self.page > 15:
            return
        url = response.url
        self.browser.delete_all_cookies()
        try:
            for cookie in self.cookies:
                self.browser.add_cookie(cookie)
        except:
            pass
        self.cookies = self.browser.get_cookies()
        self.browser.get(url)
        time.sleep(random.random()*2)
        while True:
            if "login.taobao.com" in self.browser.current_url:
                self.cookies = login(self.browser,self.username,self.password)
                time.sleep(random.random()*2)
                try:
                    self.browser.switch_to.alert.accept()
                except:
                    pass
                url = response.url
                self.browser.delete_all_cookies()
                try:
                    for cookie in self.cookies:
                        self.browser.add_cookie(cookie)
                except:
                    pass
                self.cookies = self.browser.get_cookies()
                time.sleep(random.random()*2)
            else:
                break
        #等待商品加载
        try:
            items = WebDriverWait(self.browser,10,1).until(
                lambda x: self.browser.find_element_by_xpath('//div[@class="grid g-clearfix"]/div[@class="items"]')
            )
            page_html = self.browser.page_source
        except:
            pass
        else:
            sales = re.findall(r'<div\sclass="deal-cnt".*?>(.*?)</div>', page_html)
            hrefs = re.findall(r'<a\sclass="pic-link J_ClickStat J_ItemPicA".*?href="(.*?)".*?>', page_html)
            n_item = len(hrefs)
            for i in range(n_item):
                item = TaobaospiderItem()
                #销量（收货人数）
                sale = sales[i].replace('人收货','')
                #商品详情链接
                href = hrefs[i]
                self.browser.get(href)
                time.sleep(random.random()*2)
                model, store, versions = "", "",{}
                if "detail.tmall.com" in href:
                    model,store,versions = self.parse_tm(i,href)
                elif "item.taobao.com" in href:
                    model,store,versions = self.parse_tb(i,href)
                item['model'] = model
                item['store'] = store
                item['sale'] = sale
                item['i'] = i + 1
                item['page'] = self.page
                item['ptotal'] = n_item
                item['versions'] = versions
                print(f'{item["i"]} / {item["page"]} 共{item["ptotal"]}')
                yield item
        self.page = self.page + 1
        yield scrapy.Request(url=self.base_url.format((self.page-1)*44),cookies=self.cookies,callback=self.parse)

    def parse_tm(self,index,url):
        #机型（名称+型号）
        try:
            model = WebDriverWait(self.browser,10,1).until(
                lambda x: self.browser.find_element_by_xpath('//*[@id="J_AttrUL"]/li[contains(text(),"产品名称")][last()]')
            )
            model = model.get_attribute('title')
        except:
            model = ""
        #店铺
        try:
            store = self.browser.find_element_by_xpath('//a[@class="slogo-shopname"]').text
        except:
            store = ""
        #版本-价格
        select_opt(self.browser) #组合可选套餐（非分类标准，固定为可选第一项）
        try:
            version = {}
            versions = self.browser.find_elements_by_xpath('//ul[@data-property="存储容量"]/li[not(contains(@class,"stock"))]')
            for v in versions:
                v_str = v.text.replace('\n已选中','')
                if 'selected' not in v.get_attribute('class'):
                    self.browser.execute_script("arguments[0].click();",v.find_element_by_tag_name('a'))
                time.sleep(random.random()*1)
                price = self.browser.find_elements_by_xpath('//dl[not(@style="display: none;")]//span[@class="tm-price"]')[-1].text
                version[v_str] = price
        except Exception as e:
            version = {}
        return model,store,version

    def parse_tb(self,index,url):
        #机型（名称+型号）
        try:
            time.sleep(random.random()*2)
            ps = self.browser.find_elements_by_xpath('//ul[contains(@class,"attributes-list")]/li[1]/p')
            if len(ps) == 0:
                raise Exception
            model = ""
            for p in ps:
                model = model + p.get_attribute('title') + " "
        except:
            brand, type = "", ""
            try:
                brand = self.browser.find_element_by_xpath('//ul[@class="attributes-list"]/li[starts-with(text(),"品牌")][1]').get_attribute('title')
                try:
                    type = self.browser.find_element_by_xpath('//ul[@class="attributes-list"]/li[contains(text(),"型号") and not(starts-with(text(),"CPU型号"))][1]').get_attribute('title')
                except:
                    type = ""
            except:
                brand = ""
            model = brand + " " + type
        #店铺
        try:
            store = self.browser.find_element_by_xpath('//div[@class="tb-shop-name"]//a[1]').get_attribute('title')
        except:
            try:
                store = self.browser.find_element_by_xpath('//a[@class="shop-name-link"]').get_attribute('title')
            except:
                store = ""
        #版本-价格
        select_opt(self.browser) #组合可选套餐（非分类标准，固定为可选第一项）
        time.sleep(random.random()*2)
        try:
            version = {}
            versions = self.browser.find_elements_by_xpath('//ul[@data-property="存储容量"]/li[not(contains(@class,"stock"))]')
            for v in versions:
                v_str = v.text
                if 'selected' not in v.get_attribute('class'):
                    self.browser.execute_script("arguments[0].click();",v.find_element_by_tag_name('a'))
                time.sleep(random.random()*2)
                price = self.browser.find_elements_by_xpath('//em[@class="tb-rmb-num"]')[-1].text
                version[v_str] = price
        except:
            version = {}
        return model,store,version



