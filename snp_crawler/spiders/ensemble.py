# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import json
from snp_crawler.items import EnsembleVariationItem
from snp_crawler.item_generators import GeneratorFactory
import time


class EnsembleSpider(scrapy.Spider):
    name = 'ensemble'
    allowed_domains = ['grch37.rest.ensembl.org']
    start_urls = []
    api_host = 'http://grch37.rest.ensembl.org/variation/homo_sapiens'
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    default_max_per_batch = 500
    store_keys = ['name', 'source', 'mappings', 'MAF', 'ancestral_allele', 'minor_allele', 'ambiguity',
                  'clinical_significance', 'var_class', 'synonyms', 'evidence', 'most_severe_consequence',
                  'phenotypes', 'genotypes', 'populations', 'population_genotypes']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        if 'batch_num' not in kwargs:
            kwargs['batch_num'] = EnsembleSpider.default_max_per_batch
        self._generator = GeneratorFactory.get_generator(self, **kwargs)

    def start_requests(self):
        if self._generator is not None:
            for ids in self._generator.generate():
                query = {'ids': ids}
                yield Request(self.get_api_url(), method='POST', headers=self.headers, body=json.dumps(query), dont_filter=True)
        return None

    def parse(self, response):
        js = json.loads(response.body_as_unicode())
        for rs in js:
            data = dict([(x, js[rs][x]) for x in self.store_keys if x in js[rs]])
            item = EnsembleVariationItem(data)
            item['_id'] = rs
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            yield item

    def get_api_url(self):
        query = self.get_spider_conf('query')
        if query:
            query = ['%s=%s' % (k, v) for k, v in query.items()]
            url = self.api_host + '?' + '&'.join(query)
        else:
            url = self.api_host
        return url

    def get_spider_conf(self, field=None):
        conf = self.settings['SPIDER_SETTINGS'][self.name] if self.settings['SPIDER_SETTINGS'][self.name] else {}
        if field:
            return conf[field] if field in conf else None
        return conf
