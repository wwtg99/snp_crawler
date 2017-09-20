# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from snp_crawler.items import DbSnpItem
import time
import os


class DbsnpSpider(scrapy.Spider):
    name = 'dbsnp'
    allowed_domains = ['eutils.ncbi.nlm.nih.gov']
    start_urls = []
    api_host = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    headers = None
    max_per_batch = 50

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self._rslist = kwargs['rs'] if 'rs' in kwargs else None
        self._file = kwargs['file'] if 'file' in kwargs else None

    def start_requests(self):
        if self._rslist:
            # from argument rs=
            yield self.from_rs_list()
        elif self._file:
            # from argument file=
            if os.path.exists(self._file):
                yield from self.from_rs_file()
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
        available_keys = ['ALLELE_ORIGIN', 'GLOBAL_MAF', 'CLINICAL_SIGNIFICANCE', 'GENE', 'ACC', 'CHR',
                          'VALIDATED', 'CREATE_BUILD_ID', 'MODIFIED_BUILD_ID', 'SNP_CLASS', 'CONTIGPOS']
        if len(lines) <= 0:
            return None
        item = DbSnpItem()
        item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        item['_searchable'] = ['_id', 'name', 'gene', 'clinical_significance', 'updated_at']
        for line in lines:
            kv = line.split('=')
            if len(kv) == 2:
                key = kv[0]
                if key == 'SNP_ID':
                    item['_id'] = 'rs' + kv[1]
                    item['name'] = item['_id']
                elif key == 'CHROMOSOME BASE POSITION':
                    item['pos'] = kv[1]
                elif key in available_keys:
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

    def from_rs_list(self):
        """
        Load rs list from -a rs=rs1,rs2,...
        :return:
        """
        query = {'id': self._rslist, 'db': 'snp', 'report': 'docset'}
        return Request(self.get_api_url(query), method='GET', headers=self.headers, dont_filter=True)

    def from_rs_file(self):
        """
        Load rs from file use -a file=rs_file_path
        Each rs per line or rs in the first column.
        :return:
        """
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
                    query = {'id': ','.join(rs), 'db': 'snp', 'report': 'docset'}
                    yield Request(self.get_api_url(query), method='GET', headers=self.headers, dont_filter=True)
                    i = 0
                    rs = []
            if len(rs) > 0:
                query = {'id': ','.join(rs), 'db': 'snp', 'report': 'docset'}
                yield Request(self.get_api_url(query), method='GET', headers=self.headers, dont_filter=True)
