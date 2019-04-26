# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from cartoon import settings
from scrapy.exceptions import DropItem
import os


class CartoonPipeline(object):
    def process_item(self, item, spider):
        return item


class ImagePipleline(ImagesPipeline):
    def get_media_requests(self, item, info):
        image_url = item['image_url']
        meta = {'image_title': item['image_title'],
                'subFilename': item['subFilename']}
        yield Request(url=image_url, meta=meta)

    def file_path(self, request, response=None, info=None):
        # 把漫画title   章节name  imagename  层层链接
        # 获取自定义路径
        title = request.meta.get('image_title','标题未定义')
        #获取文件夹路径
        subFilename = request.meta.get('subFilename')
        #获取图片名
        file_name = title + '.jpg'
        # 将文件夹路径与文件名组合
        # image_path=os.path.join(subFilename,file_name)      #'F:\\kuku漫画/魔王的父亲/魔王的父亲_恶魔奶爸1话\\第11页.jpg'    报错
        image_path= subFilename + '/' + file_name            #'F:\\kuku漫画/魔王的父亲/魔王的父亲_恶魔奶爸1话/第11页.jpg'
        print(image_path)
        return image_path


    def item_completed(self, results, item, info):
        # results:
        #[(True,
        # {'url': 'http://n9.1whour.com/kuku5comic5/msdfl/25/cccc_0171IW.jpg',
        # 'path': '第17页.jpg',
        # 'checksum': '02337ea817cf1b8af2d739777d616a51'}
        # )]

        for ok, value in results:
            if ok:
                if not value['path']:
                    raise DropItem('图片下载失败')
        return item

