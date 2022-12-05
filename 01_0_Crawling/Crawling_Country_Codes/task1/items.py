# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Country_Code(scrapy.Item):
    # define the fields for your item here like:
    iso_3 = scrapy.Field()
    continent = scrapy.Field()
    name = scrapy.Field()
    # iso_2 = scrapy.Field()


# class Country_Country_Item(scrapy.Item):
# define the fields for your item here like:
# exports_from = scrapy.Field()
# exports_to = scrapy.Field()
# exports = scrapy.Field()
# exported_items = scrapy.Field()
# year = scrapy.Field()
# rank = scrapy.Field()
# url = scrapy.Field()


# class MovieItem(scrapy.Item):
#     # define the fields for your item here like:
#     title = scrapy.Field()
#     directors = scrapy.Field()
#     directors_url = scrapy.Field()
#     plot = scrapy.Field()
#     actors = scrapy.Field()

# class DirectorItem(scrapy.Item):
#     # define the fields for your item here like:
#     name = scrapy.Field()
#     birthDate = scrapy.Field()
#     deathDate = scrapy.Field()
#     biography = scrapy.Field()
