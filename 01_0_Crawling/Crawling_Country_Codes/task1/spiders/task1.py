import scrapy
import urllib
from ..items import Country_Code
from scrapy.http.request import Request
import json
import ast
import requests
from scrapy.crawler import CrawlerProcess


class countryCode(scrapy.Spider):

    # name identifies the parser
    name = "countryCode"
    custom_settings = {
        "ITEM_PIPELINES": {
            "task1.pipelines.tradePipeline": 300,
        }
    }

    def start_requests(self):
        yield scrapy.Request(url="https://country-code.cl/", callback=self.parse)

    def parse(self, response):
        code_Obj = Country_Code()
        continents = response.xpath("//tbody/tr/td[1]/text()").extract()
        names = response.xpath("//tbody/tr/td[3]/span[1]/text()").extract()
        isos = response.xpath("//tbody/tr/td[5]/text()").extract()

        for i, j, k in zip(continents, names, isos):
            code_Obj["iso_3"] = k
            code_Obj["continent"] = i
            code_Obj["name"] = j
            yield code_Obj
