# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CartoonItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    image_title = scrapy.Field()
    image_url = scrapy.Field()
    section_name = scrapy.Field()
    manhua_name = scrapy.Field()
    image_paths = scrapy.Field()