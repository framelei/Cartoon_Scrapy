# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CartoonItem(scrapy.Item):

    #大类的标题和url      漫画名
    parentTitle = scrapy.Field()
    parentUrl = scrapy.Field()

    #小类的标题和url      章节名
    subTitle = scrapy.Field()
    subUrl = scrapy.Field()

    # 小类目录存储路径,最终存储时提供路径    漫画的最终路径
    subFilename = scrapy.Field()

    #漫画标题、url                           漫画的名称、每个图片url

    detail_url = scrapy.Field()
    image_title = scrapy.Field()

    image_url = scrapy.Field()