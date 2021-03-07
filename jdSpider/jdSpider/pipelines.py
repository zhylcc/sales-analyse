# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv

class JdspiderPipeline(object):
    def open_spider(self, spider):
        self.file = open("../source/jd.csv","a",encoding='utf-8',newline="")
        self.log = open("../log/jd_spider.txt",'a',encoding='utf-8')
        self.write = csv.writer(self.file)
        self.write.writerow(("model","store","versions","sale"))

    def process_item(self, item, spider):
        self.write.writerow((item['model'],item['store'],item['versions'],item['sale']))
        self.log.write(f'{item["i"]} / {item["page"]} {item["ptotal"]}'+'\n')
        return item

    def close_spider(self, spider):
        self.file.close()
        self.log.close()
        spider.browser.quit()
