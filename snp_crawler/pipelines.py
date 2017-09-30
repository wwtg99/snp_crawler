# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import requests
import json
import logging


class SnpCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class MongodbPipeline(object):
    """
    If _id exists in item, use replace_one by _id, or use insert_one.
    """

    def __init__(self, mongo_uri, mongo_db, collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection = collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            collection=crawler.settings.get('MONGO_COLLECTION')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if not self.collection:
            self.collection = spider.name
        data = dict(item)
        if '_id' in data:
            self.db[self.collection].replace_one({'_id': item['_id']}, data, upsert=True)
        else:
            self.db[self.collection].insert_one(data)
        return item


class ElasticsearchPipeline(object):
    """
    Get fields in _searchable of item, store by Elasticsearch api.
    If _id exists in item, use _id as id, or use auto generated id.
    """
    def __init__(self, host, index, type):
        self.host = host
        self.index = index
        self.type = type

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('ELASTICSEARCH_HOST'),
            index=crawler.settings.get('ELASTICSEARCH_INDEX'),
            type=crawler.settings.get('ELASTICSEARCH_TYPE')
        )

    def process_item(self, item, spider):
        if not self.type:
            self.type = spider.name
        conf = spider.settings['SPIDER_SETTINGS'][spider.name] if spider.settings['SPIDER_SETTINGS'][spider.name] else {}
        if conf['elasticsearch_fields']:
            fields = conf['elasticsearch_fields']
            data = {}
            for f in fields:
                if f in item:
                    data[f] = item[f]
            if '_id' in data:
                fid = data['_id']
                del data['_id']
                res = requests.put('/'.join([self.host, self.index, self.type, fid]), json.dumps(data))
            else:
                res = requests.post('/'.join([self.host, self.index, self.type]), json.dumps(data))
            if res.status_code >= 400:
                logging.error('Store Elasticsearch failed for %s, return message %s' % (json.dumps(data), res.text))
        return item
