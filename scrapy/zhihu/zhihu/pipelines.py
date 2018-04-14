# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from zhihu.items import UserItem_json, UserItem_page

class Item_pagePipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, UserItem_page):
            if item["locations"]: item["locations"] = item["locations"][1]
            if item["favorited_count"]: item["favorited_count"] = item["favorited_count"][-1][:-4]
            if item["thank_from_count"]: item["thank_from_count"] = item["thank_from_count"][-3][2:-4]
        return item





class MongoPipeline(object):
    collection_name1 = 'users0'  #page data
    collection_name2 = 'users1'  #json data

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, UserItem_page):
            self.db[self.collection_name1].update({'url_token': item['url_token']}, dict(item), True)
        else:
            self.db[self.collection_name2].update({'url_token': item['url_token']}, dict(item), True)

        print("insert into mogodb")

        return item