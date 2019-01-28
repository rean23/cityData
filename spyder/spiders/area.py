# -*- coding: utf-8 -*-
import scrapy
from spyder.items import SpyderItem
from scrapy.http import Request
from pyquery import PyQuery as pq
from os import path


class AreaSpider(scrapy.Spider):
    name = 'area'
    allowed_domains = ['www.stats.gov.cn']
    start_urls = ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/']

    def parse(self, response):
        # 生成pyquery实例
        doc = pq(response.text);

        # 生成item
        item = SpyderItem();

        provinces = doc('table:eq(4) tr:gt(2) a').items();

        level = 1;

        for province in provinces:
            # 获取地址
            provinceUrl = province.attr.href;

            # 获取省份code
            item['code'] = provinceUrl[:-5];

            # 获取省份名称
            item['name'] = province.text().strip();

            # 获取请求地址
            item['url'] = response.url + provinceUrl;

            item['level'] = level;


            yield item;
            yield Request(url=item['url'], callback=self.parseChildren,
                          meta={'level': level + 1, 'parentCode': item['code']});

    def parseChildren(self, response):

        # 生成实例
        doc = pq(response.text);

        # 创建item
        item = SpyderItem();

        # 获取meta对象
        meta = response.meta;

        # 获取列表
        list = doc('table:eq(4) tr:gt(0)').items();

        # 获取基础网址
        url = path.dirname(response.url) + '/';

        # 获取级别
        level = meta['level'];

        for row in list:

            if(row.find('td a').length > 0):
                line = row.find('td a');
                item['name'] = line.eq(1).text();
            else:
                line = row.find('td');
                item['name'] = line.eq(2).text();

            item['code'] = line.eq(0).text();

            item['level'] = level;


            # 获取请求地址
            href = row.find('td a').attr.href;
            if (href is None):
                item['url'] = None;
            else:
                item['url'] = url + href;

            yield item;

            if (item['url'] is not None):
                yield Request(url=item['url'], callback=self.parseChildren,
                              meta={'level': level + 1, 'code': item['code']});
