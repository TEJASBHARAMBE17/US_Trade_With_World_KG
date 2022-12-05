from itemadapter import ItemAdapter
import json
from task1.items import Country_Code


class tradePipeline(object):
    def __init__(self):
        # self.filename_1 = "TejasSujit_Bharambe_t01_exports.jsonl"
        # self.file_1 = open(self.filename_1, "wb")

        self.filename_2 = "../../../Output/TejasSujit_Bharambe_hw01_country_code.jsonl"
        self.file_2 = open(self.filename_2, "wb")

        # self.filename_3 = "TejasSujit_Bharambe_hw01_director.jsonl"
        # self.file_3 = open(self.filename_3, "wb")

    def process_item(self, item, spider):

        data = json.dumps(dict(item), ensure_ascii=False) + "\n"

        # if isinstance(item, Country_Country_Item):
        #     self.file_1.write(data.encode("utf-8"))
        #     return item

        if isinstance(item, Country_Code):
            self.file_2.write(data.encode("utf-8"))
            return item

        # elif isinstance(item, DirectorItem):
        #     self.file_3.write(data.encode("utf-8"))
        #     return item

    def close_spider(self, spider):
        # self.file_1.close()
        self.file_2.close()
        # self.file_3.close()
