# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from snp_crawler.items import GwasAssociationItem
from snp_crawler.utils import Configurable
import os


class GwasCatelogSpider(scrapy.Spider, Configurable):
    name = 'gwas_catelog'
    allowed_domains = ['www.ebi.ac.uk']
    start_urls = ['http://www.ebi.ac.uk/gwas/api/search/downloads/alternative']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        if 'file' in kwargs:
            self._file = kwargs['file']
        else:
            self._file = None

    def start_requests(self):
        if self._file is not None:
            # load from file
            url = 'file:///' + os.path.abspath(self._file).replace('\\', '/')
            self.logger.info('Load from file %s' % self._file)
            yield Request(url, dont_filter=True)
        else:
            for url in self.start_urls:
                yield Request(url, dont_filter=True)

    def parse(self, response):
        cont = response.text
        lines = cont.split('\n')
        # remove header
        del lines[0]
        for line in lines:
            if not line:
                continue
            cols = line.split('\t')
            l = list(map(lambda x: x.strip() if x.strip() else None, cols))
            item = GwasAssociationItem()
            header = self.get_spider_conf('header', [])
            for i in range(len(header)):
                item[header[i]] = l[i] if l[i] != 'NR' else None
            yield item

