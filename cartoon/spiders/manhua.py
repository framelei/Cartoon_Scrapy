# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urljoin
import re
import os
from cartoon.items import CartoonItem


class ManhuaSpider(scrapy.Spider):
    name = 'manhua'
    allowed_domains = ['comic.kukukkk.com']
    start_urls = ['http://comic.kukukkk.com/']

    # rules = (
    #     #为排除新增章节的影响使用/\d+/$
    #     Rule(LinkExtractor(allow=r'comiclist/\d+/$'), callback='section_url'),
    # )

    def parse(self, response):
        '''
        通过漫画首页解析漫画url、title
        '''
        #第一次存储信息，用于meta传参，传递了 大title、url、文件路径   共3个参数
        infos = []

        parentTitle =  response.xpath('//dl[1]/dd/a/text()').extract()      # ['火影忍者', '海贼王',]
        parentUrl = response.xpath('//dl[1]/dd/a/@href').extract()          #['/comiclist/3/',]

        for i in range(len(parentTitle)):
            parentFilename = 'F:\kuku漫画' + '/' +  parentTitle[i]

            # 如果目录不存在，则创建目录     必须一层一层创建（主文件夹-子文件夹），否则无法运行     亲测
            if not os.path.exists(parentFilename):
                os.mkdir(parentFilename)

            #保存大类的title、urls 、文件路径
            item = CartoonItem()
            item['parentTitle'] = parentTitle[i]
            item['parentUrl'] = urljoin(response.url,parentUrl[i])
            item['subFilename'] = parentFilename
            infos.append(item)

        for info in infos:
            yield scrapy.Request(url=info['parentUrl'],meta={'info':info},callback=self.second_parse)

    def second_parse(self,response):
        '''
        在漫画章节列表页，获取章节title、url
        :param response:
        :return:
        '''

        #第二次存储信息，用于meta传参，传递了上边3个参数  +   subTitle、subUrl、重新封装路径 共5个参数
        info = response.meta['info']
        objs = []

        subTitle = response.xpath('//dl[@id="comiclistn"]/dd/a[1]/text()').extract()     #['火影忍者_Naruto_Vol_1',]
        subUrl = response.xpath('//dl[@id="comiclistn"]/dd/a[1]/@href').extract()       #[ '/comiclist/3/66867/1.htm','/comiclist/3/67024/1.htm',]

        for i in range(len(subTitle)):
            #有些章节title存在分隔符，对文件夹产生干扰。   eg:魔王的父亲/恶魔奶爸1话
            #文件夹不能包含特殊符号如 *                    eg:火影忍者[589]秽土转生之术*解
            #                         :                    eg:海贼王[860]10:00開宴
            #                         ?                    eg:海贼王[884]是谁?
            parentFilename = info['subFilename'] + '/' + subTitle[i].replace('/','_').replace('*','_').replace(':','_').replace('？','')
            # 如果目录不存在，则创建目录
            if not os.path.exists(parentFilename):
                os.mkdir(parentFilename)

            #保存大类的title、urls + 小类title、urls、路径
            item = CartoonItem()
            item['parentTitle'] = info['parentTitle']
            item['parentUrl'] = info['parentUrl']
            item['subFilename'] = parentFilename
            item['subTitle'] = subTitle[i]
            item['subUrl'] = urljoin(response.url,subUrl[i])
            objs.append(item)

        for obj in objs:
            yield scrapy.Request(url=obj['subUrl'],meta={'obj':obj},callback=self.detail_parse)


    def detail_parse(self,response):
        #在详情页，获取漫画总页数，当前页。

        obj = response.meta['obj']
        #第三次存储信息，用于meta传参，传递了大title、url、subTitle、subUrl、重新封装路径  + image_title、detail_url共7个参数
        datas = []

        # for obj in objs:
        detail_info = response.xpath('//tr/td/text()').extract_first()  #'火影忍者_Naruto_Vol_1 | 共97页 | 当前第1页 | 跳转至第 '
        if detail_info:
            total_num = re.findall(' 共(\d+)页 ',detail_info)
            total_num = int(''.join(total_num))     #将List转为int     ['97']   97
            #url = response.url                      #'http://comic.kukukkk.com/comiclist/3/3/1.htm'
            for i in range(1,total_num):     #舍弃最后一页
                detail_url = '{num}.htm'.format(num=i)
                image_title = '第{num}页'.format(num=i)

                #保存大类的title、urls 、小类title、urls、路径 + image_title、image所在的url页面
                item = CartoonItem()
                item['image_title'] = image_title
                item['detail_url'] = urljoin(response.url,detail_url)
                #引入传递进来的数据
                item['parentTitle'] = obj['parentTitle']
                item['parentUrl'] = obj['parentUrl']
                item['subTitle'] = obj['subTitle']
                item['subUrl'] = obj['subUrl']
                item['subFilename'] = obj['subFilename']
                datas.append(item)

        for data in datas:
            yield scrapy.Request(data['detail_url'],callback=self.get_image_url,meta={'datas':data})

    def get_image_url(self,response):
        '''
        通过
        :param response: image的实际url
        :return:
        '''
        data = response.meta['datas']

        url_js =  response.xpath('//script/text()').extract_first()
        #'\r\ndocument.write("<a href=\'/comiclist/3/3/2.htm\'>
        # <IMG SRC=\'"+m201304d+"comic/kuku2comic/Naruto/01/01_01.JPG\'>
        # </a><span style=\'display:none\'><img src=\'"+m201304d+"comic/kuku2comic/Naruto/01/01_02.JPG\'></span>");\r\n'

        base_url = re.findall('.*?\+"(.*?)\'>.*',url_js)   #结果不容易匹配，慢慢分析不要急     错过
        detail_url ='http://n9.1whour.com/' + ''.join(base_url)

        #保存大类的title、urls 、小类title、urls、路径 、image_title、image所在的url页面 + image_url
        items = CartoonItem()
        items['image_url'] = detail_url
        #引入传递进来的数据  #使用了多次meta，亲测一次取不到
        items['parentTitle'] = data['parentTitle']
        items['parentUrl'] = data['parentUrl']
        items['subTitle'] = data['subTitle']
        items['subUrl'] = data['subUrl']
        items['subFilename'] = data['subFilename']
        items['image_title'] = data['image_title']
        items['detail_url'] = data['detail_url']

        return items
