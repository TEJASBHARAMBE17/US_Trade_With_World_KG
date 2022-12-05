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
        # with open(
        #     "../../../Output/TejasSujit_Bharambe_hw01_country_code - trimmed.jsonl",
        #     "r",
        #     encoding="utf-8",
        # ) as json_file:
        #     for line in json_file:
        #         json_list.append(json.loads(line))

        # mapping_dict = {}

        # for data in json_list:
        #     mapping_dict[data["iso_3"].lower()] = {
        #         "continent": data["continent"].lower(),
        #         "name": data["name"].lower(),
        #     }

        # countries_permutations = list(
        #     itertools.permutations(list(mapping_dict.keys()), 2)
        # )

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

        years = [
            "2000",
            "2001",
            "2002",
            "2003",
            "2004",
            "2005",
            "2006",
            "2007",
            "2008",
            "2009",
            "2010",
            "2011",
            "2012",
            "2013",
            "2014",
            "2015",
            "2016",
            "2017",
            "2018",
            "2019",
            "2020",
        ]

        for year in years:
            c_c_Obj = Country_Country_Item()

            exports_from = response.url.split("/")[-3]
            exports_to = response.url.split("/")[-1]

            c_c_Obj["exports_from"] = exports_from
            c_c_Obj["exports_to"] = exports_to
            c_c_Obj["exports"] = response.xpath(
                '//*[@id="Profile"]/div[2]/div[1]/header/div[1]/div[1]/div[2]/p[1]/span[3]/span[1]/a/text()'
            ).get()
            c_c_Obj["exports_year"] = year

            url_inner = (
                # "https://app-hog.oec.world/olap-proxy/data?cube=trade_i_baci_a_92&Exporter+Country="
                "https://oec.world/olap-proxy/data?cube=trade_i_baci_a_92&Exporter+Country="
                + response.meta["codes"][exports_from]["continent"]
                + exports_from
                + "&Importer+Country="
                + response.meta["codes"][exports_to]["continent"]
                + exports_to
                + "&Year="
                + year
                + "&drilldowns=HS4&measures=Trade+Value&parents=true&locale=en&q=1,1"
            )

            page = requests.get(url_inner)
            trade_dict = ast.literal_eval(page.content.decode("utf-8"))
            c_c_Obj["exported_items"] = trade_dict["data"]
            print(
                "\n\n\n check",
                exports_from + response.meta["codes"][exports_from]["continent"],
                exports_to + response.meta["codes"][exports_to]["continent"],
            )
            yield c_c_Obj
