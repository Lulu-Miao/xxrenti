# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request

from xxrenti.items import XxrentiItem


class RentiSpider(scrapy.Spider):
    name = 'renti'
    allowed_domains = ['xxrenti.in']
    start_urls = ['http://www.xxrenti.in/yazhourenti/',
                  'http://www.xxrenti.in/oumeirenti/',
                  'http://www.xxrenti.in/guomosipai/',
                  'http://www.xxrenti.in/hanguorenti/',
                  'http://www.xxrenti.in/ribenrenti/',
                  'http://www.xxrenti.in/a4you/',
                  'http://www.xxrenti.in/dadanrenti/']

    def parse(self, response):
        for href, name in zip(response.xpath(r'//div[@class="list_pic"]//a/@href').extract(),
                              response.xpath(r'//div[@class="list_pic"]//a/@title').extract()):
            yield Request(response.urljoin(href), callback=self.parse_img, meta={'name': name})

        if response.url.endswith('/'):
            max_page = int(response.xpath(r'//div[@class="pages"]/a[last()-1]/text()').extract_first())
            for index in range(2, max_page+1):
                # http://www.xxrenti.in/oumeirenti/2.html
                url = response.url + str(index) + '.html'
                yield Request(url, callback=self.parse)

    def parse_img(self, response):
        for url in response.xpath(r'//div[@class="main"]/div/a/img/@src').extract():
            item = XxrentiItem()
            item['name'] = response.meta['name']
            item['url'] = url
            yield item

        if response.url.find('_') == -1:
            # 最后一页所在的div是不固定的，要轮循查找
            for i in range(3, 11):
                try:
                    max_page = int(response.xpath(r'//div[@class="main"]/div[{}]//a[last()-1]/text()'.format(i)).extract_first())
                except TypeError:
                    continue
                else:
                    break

            for index in range(2, max_page+1):
                # http://www.xxrenti.in/oumeirenti/2018/0825/3276_2.html
                url = response.url[:response.url.rindex('.')] + '_' + str(index) + '.html'
                yield Request(url, callback=self.parse_img, meta={'name': response.meta['name']})
