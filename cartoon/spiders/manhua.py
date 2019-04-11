# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urljoin
import re
from cartoon.items import CartoonItem


class ManhuaSpider(CrawlSpider):
    name = 'manhua'
    allowed_domains = ['comic.kukukkk.com']
    start_urls = ['http://comic.kukukkk.com/']

    rules = (
        #为排除新增章节的影响使用/\d+/$
        Rule(LinkExtractor(allow=r'comiclist/\d+/$'), callback='section_url', follow=True),
    )

    def section_url(self, response):
        '''
        通过漫画详情页解析漫画章节url、title
        :param response: 漫画详情页
        :return:章节的title、章节的url
        '''
        section_infos = response.xpath('//dl/dd/a[1]')
        manhua_name =  response.xpath('//dl/dd[1]/a[1]/text()').extract_first()

        for info in section_infos:
            section_url = info.xpath('./@href').extract_first()
            section_title = info.xpath('./text()').extract_first()
            yield scrapy.Request(url=urljoin(response.url,section_url),meta={'section_title':section_title,'manhua_name':manhua_name},callback=self.detail_url)

    def detail_url(self,response):
        '''
        在章节详情页，获取漫画总页数，当前页。
        :param response:
        :return: 每张image的url、title
        '''

        section_name = response.meta['section_title']
        manhua_name = response.meta['manhua_name']
        detail_info = response.xpath('//tr/td/text()').extract_first()  #'火影忍者_Naruto_Vol_1 | 共97页 | 当前第1页 | 跳转至第 '
        if detail_info:
            # detail_title = re.findall(' 当前(.*?) ',detail_info)
            total_num = re.findall(' 共(\d+)页 ',detail_info)
            total_num = int(''.join(total_num))     #将List转为int     ['97']   97
            #url = response.url                      #'http://comic.kukukkk.com/comiclist/3/3/1.htm'
            for page_num in range(1,total_num):     #舍弃最后一页
                index_url = '{num}.htm'.format(num=page_num)
                detail_title = '第{num}页'.format(num=page_num)
                yield scrapy.Request(urljoin(response.url,index_url),callback=self.get_detail_url,meta={'detail_title':detail_title,'section_name':section_name,'manhua_name':manhua_name})

    def get_detail_url(self,response):
        '''
        通过
        :param response: image的实际url
        :return:
        '''
        url_js =  response.xpath('//script/text()').extract_first()
        #'\r\ndocument.write("<a href=\'/comiclist/3/3/2.htm\'>
        # <IMG SRC=\'"+m201304d+"comic/kuku2comic/Naruto/01/01_01.JPG\'>
        # </a><span style=\'display:none\'><img src=\'"+m201304d+"comic/kuku2comic/Naruto/01/01_02.JPG\'></span>");\r\n'

        base_url = re.findall('.*?\+"(.*?)\'>.*',url_js)   #结果不容易匹配，慢慢分析不要急     错过
        detail_url ='http://n9.1whour.com/' + ''.join(base_url)
        # print(detail_url)
        items = CartoonItem()
        items['image_title'] = response.meta['detail_title']
        items['image_url'] = detail_url
        items['section_name'] = response.meta['section_name']   #注意章节的传递方式  使用了两次meta，亲测一次取不到
        items['manhua_name'] = response.meta['manhua_name']
        return items
