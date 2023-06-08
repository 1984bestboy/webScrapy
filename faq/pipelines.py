# Define your item pipelines here
# 定義items資料的後續處理，像是清理、儲存至資料庫或檔案等。
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class FaqPipeline:
    def process_item(self, item, spider):
        return item
