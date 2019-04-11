# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from cartoon import settings
import os


class CartoonPipeline(object):
    def process_item(self, item, spider):
        return item


class ImagePipleline(ImagesPipeline):
    def get_media_requests(self, item, info):
        image_url = item['image_url']
        meta = {'image_title': item['image_title'], 'section_name': item['section_name'],
                'manhua_name': item['manhua_name']}
        yield Request(url=image_url, meta=meta)

    def file_path(self, request, response=None, info=None):
        # 把漫画title   章节name  imagename  层层链接
        # 获取自定义路径
        image_store = settings.IMAGES_STORE
        manhua_name = request.meta.get('manhua_name', '漫画未命名')
        section_name = request.meta.get('section_name', '图集未命名')
        # 在自定义路径下 创建漫画文件夹
        manhua = os.path.join(image_store, manhua_name)
        if not os.path.exists(manhua):
            os.makedirs(manhua)
            # 在漫画文件夹下 创建章节文件夹
            section = os.path.join(manhua, section_name)
            if not os.path.exists(section):
                os.makedirs(section)
                # 写入漫画title内容
                title = request.meta.get('image_title', '图片未命名')
                file_name = title + '.jpg'
                print(file_name, '*' * 30)
                return file_name


    def item_completed(self, results, item, info):
        for ok, value in results:
            if ok:
                image_path = value['path']
        item['image_paths'] = image_path
        return item
