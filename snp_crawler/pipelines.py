# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import requests
import json
import logging
from elasticsearch import Elasticsearch
from elasticsearch import TransportError
from scrapy.exceptions import DropItem


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
            res = self.db[self.collection].insert_one(data)
            # add auto id
            if res and res.inserted_id:
                item['_id'] = str(res.inserted_id)
        return item


class ElasticsearchPipeline(object):
    """
    Get fields in _searchable of item, store by Elasticsearch api.
    If _id exists in item, use _id as id, or use auto generated id.
    """
    def __init__(self, hosts, index, type, prefix):
        self.hosts = hosts
        self.index = index
        self.type = type
        self.prefix = prefix
        self.elasticsearch = Elasticsearch(hosts=hosts)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            hosts=crawler.settings.get('ELASTICSEARCH_HOSTS'),
            index=crawler.settings.get('ELASTICSEARCH_INDEX'),
            type=crawler.settings.get('ELASTICSEARCH_TYPE'),
            prefix=crawler.settings.get('ELASTICSEARCH_INDEX_PREFIX')
        )

    def process_item(self, item, spider):
        if not self.index:
            self.index = self.prefix + spider.name if self.prefix else spider.name
        if not self.type:
            self.type = spider.name
        fields = spider.get_spider_conf('elasticsearch_fields') if hasattr(spider, 'get_spider_conf') else {}
        if fields:
            data = dict([(f, item[f]) for f in fields if f in item])
            try:
                if '_id' in data:
                    fid = data['_id']
                    del data['_id']
                    res = self.elasticsearch.index(index=self.index, doc_type=self.type, id=fid, body=data)
                else:
                    res = self.elasticsearch.index(index=self.index, doc_type=self.type, body=data)
                    # add auto id
                    if res and '_id' in res:
                        item['_id'] = res['_id']
            except TransportError as err:
                raise DropItem('Elasticsearch Error ' + json.dumps(err.info))
        return item
