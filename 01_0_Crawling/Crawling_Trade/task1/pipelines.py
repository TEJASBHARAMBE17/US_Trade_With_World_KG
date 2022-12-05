from itemadapter import ItemAdapter
import json
from task1.items import Country_Country_Item


class tradePipeline(object):
    def __init__(self):
        self.filename_1 = "../../../Output/TejasSujit_Bharambe_hw01_exports.jsonl"
        self.file_1 = open(self.filename_1, "wb")

    def process_item(self, item, spider):

        data = json.dumps(dict(item), ensure_ascii=False) + "\n"

        if isinstance(item, Country_Country_Item):
            self.file_1.write(data.encode("utf-8"))
            return item

    def close_spider(self, spider):
        self.file_1.close()
