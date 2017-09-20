# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import json
from snp_crawler.items import EnsembleVariationItem
import time
import os


class EnsembleSpider(scrapy.Spider):
    name = 'ensemble'
    allowed_domains = ['grch37.rest.ensembl.org']
    start_urls = []
    api_host = 'http://grch37.rest.ensembl.org/variation/homo_sapiens'
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    max_per_batch = 500

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self._rslist = kwargs['rs'].split(',') if 'rs' in kwargs else []
        self._file = kwargs['file'] if 'file' in kwargs else None

    def start_requests(self):
        if self._rslist:
            # from argument rs=
            yield self.from_rs_list()
        elif self._file:
            # from argument file=
            if os.path.exists(self._file):
                for req in self.from_rs_file():
                    yield req
        return None

    def parse(self, response):
        js = json.loads(response.body_as_unicode())
        for rs in js:
            item = EnsembleVariationItem(js[rs])
            item['_id'] = rs
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            item['_searchable'] = ['_id', 'name', 'synonyms', 'updated_at']
            yield item

    def get_api_url(self):
        query = self.settings['ENSEMBLE_QUERY'] if self.settings['ENSEMBLE_QUERY'] else {}
        if query:
            query = ['%s=%s' % (k, v) for k, v in query.items()]
            url = self.api_host + '?' + '&'.join(query)
        else:
            url = self.api_host
        return url

    def from_rs_list(self):
        """
        Load rs list from -a rs=rs1,rs2,...
        :return:
        """
        data = {'ids': self._rslist}
        return Request(self.get_api_url(), method='POST', headers=self.headers, body=json.dumps(data), dont_filter=True)

    def from_rs_file(self):
        """
        Load rs from file use -a file=rs_file_path
        Each rs per line or rs in the first column.
        :return:
        """
        url = self.get_api_url()
        with open(self._file) as fh:
            i = 0
            rs = []
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                if line.find('\t') > 0:
                    cols = line.split('\t')
                    line = cols[0]
                elif line.find(',') > 0:
                    cols = line.split(',')
                    line = cols[0]
                rs.append(line)
                i += 1
                if i >= self.max_per_batch:
                    data = {'ids': rs}
                    yield Request(url, method='POST', headers=self.headers, body=json.dumps(data), dont_filter=True)
                    i = 0
                    rs = []
            if len(rs) > 0:
                data = {'ids': rs}
                yield Request(url, method='POST', headers=self.headers, body=json.dumps(data), dont_filter=True)

