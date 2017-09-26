# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from snp_crawler.items import DbSnpItem
from snp_crawler.item_generators import GeneratorFactory
import time


class DbsnpSpider(scrapy.Spider):
    name = 'dbsnp'
    allowed_domains = ['eutils.ncbi.nlm.nih.gov']
    start_urls = []
    api_host = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    headers = None
    default_max_per_batch = 100
    store_keys = ['ALLELE_ORIGIN', 'GLOBAL_MAF', 'CLINICAL_SIGNIFICANCE', 'GENE', 'ACC', 'CHR', 'VALIDATED',
                  'CREATE_BUILD_ID', 'MODIFIED_BUILD_ID', 'SNP_CLASS', 'CONTIGPOS']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        if 'batch_num' not in kwargs:
            kwargs['batch_num'] = DbsnpSpider.default_max_per_batch
        self._generator = GeneratorFactory.get_generator(self, **kwargs)

    def start_requests(self):
        if self._generator is not None:
            for ids in self._generator.generate():
                query = {'id': ','.join(ids), 'db': 'snp', 'report': 'docset'}
                yield Request(self.get_api_url(query), method='GET', headers=self.headers, dont_filter=True)
        return None

    def parse(self, response):
        content = response.body_as_unicode()
        lines = content.split('\n')
        data = []
        for line in lines:
            line = line.strip()
            if not line and len(data) > 0:
                item = self.parse_data_docset(data)
                if item:
                    data = []
                    yield item
            else:
                data.append(line)
        if len(data) > 0:
            yield self.parse_data_docset(data)

    def parse_data_docset(self, lines):
        if len(lines) <= 0:
            return None
        item = DbSnpItem()
        item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        item['_searchable'] = ['_id', 'name', 'gene', 'allele_origin', 'clinical_significance', 'updated_at']
        for line in lines:
            kv = line.split('=')
            if len(kv) == 2:
                key = kv[0]
                if key == 'SNP_ID':
                    item['_id'] = 'rs' + kv[1]
                    item['name'] = item['_id']
                elif key == 'CHROMOSOME BASE POSITION':
                    item['pos'] = kv[1]
                elif key in self.store_keys:
                    item[key.lower()] = kv[1]
        if '_id' in item:
            return item
        else:
            return None

    def get_api_url(self, query):
        q = self.settings['DBSNP_QUERY'] if self.settings['DBSNP_QUERY'] else {}
        query = dict(query, **q)
        if query:
            qls = ['%s=%s' % (k, v) for k, v in query.items()]
            url = self.api_host + '?' + '&'.join(qls)
        else:
            url = self.api_host
        return url
