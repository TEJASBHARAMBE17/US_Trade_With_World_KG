# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Country_Country_Item(scrapy.Item):
    # define the fields for your item here like:
    exports_from = scrapy.Field()
    exports_to = scrapy.Field()
    exports = scrapy.Field()
    exported_items = scrapy.Field()
    exports_year = scrapy.Field()
