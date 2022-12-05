import scrapy
import urllib
from ..items import Country_Country_Item
from scrapy.http.request import Request
import json
import ast
import requests
from scrapy.crawler import CrawlerProcess
import itertools


class worldTrade(scrapy.Spider):
    # name identifies the parser
    name = "worldTrade"
    custom_settings = {
        "ITEM_PIPELINES": {
            "task1.pipelines.tradePipeline": 300,
        }
    }

    def start_requests(self):

        json_list = []
        with open(
            "../../../Output/TejasSujit_Bharambe_hw01_country_code.jsonl",
            "r",
            encoding="utf-8",
        ) as json_file:
            for line in json_file:
                json_list.append(json.loads(line))

        mapping_dict = {}

        for data in json_list:
            mapping_dict[data["iso_3"].lower()] = {
                "continent": data["continent"].lower(),
                "name": data["name"].lower(),
            }

        countries_permutations = []
        for k in mapping_dict.keys():
            if k != "USA" or k != "usa":
                # countries_permutations.append(["usa", k])
                countries_permutations.append([k, "usa"])

        urls = []
        # print("\n\n\n\n", countries_permutations)
        for c1, c2 in countries_permutations:
            urls.append(
                "https://oec.world/en/profile/bilateral-country/"
                + c1
                + "/partner/"
                + c2
            )

        # urls.append("https://oec.world/en/profile/bilateral-country/usa/partner/chn")

        for url in urls:
            yield scrapy.Request(
                url=url, callback=self.parse, meta={"codes": mapping_dict}
            )

    def parse(self, response):

        c_c_Obj = Country_Country_Item()

        exports_from = response.url.split("/")[-3]
        exports_to = response.url.split("/")[-1]

        c_c_Obj["exports_from"] = exports_from
        c_c_Obj["exports_to"] = exports_to
        c_c_Obj["exports_details"] = []
        c_c_Obj["exports_details"].append(
            response.xpath('//*[@id="cp-section-312"]/div/div[2]/p[1]//text()').getall()
        )

        c_c_Obj["exports_details"].append(
            response.xpath('//*[@id="cp-section-312"]/div/div[2]/p[2]//text()').getall()
        )

        c_c_Obj["exports_details"].append(
            response.xpath('//*[@id="cp-section-312"]/div/div[2]/p[3]//text()').getall()
        )

        c_c_Obj["exports_details"].append(
            response.xpath('//*[@id="cp-section-312"]/div/div[2]/p[4]//text()').getall()
        )

        c_c_Obj["exports_details"].append(
            response.xpath('//*[@id="cp-section-312"]/div/div[2]/p[5]//text()').getall()
        )
        x = ""
        for data in c_c_Obj["exports_details"]:
            x += " ".join(map(str, data))

        c_c_Obj["exports_details"] = x
        yield c_c_Obj
