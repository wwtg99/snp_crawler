# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import json
from snp_crawler.items import DeafnessItem
from snp_crawler.item_generators import GeneratorFactory
import time
from snp_crawler.utils import Configurable
import requests


class DeafnessvdbSpider(scrapy.Spider, Configurable):
    name = 'deafnessvdb'
    allowed_domains = ['deafnessvariationdatabase.org']
    start_urls = []
    api_host = 'http://deafnessvariationdatabase.org/api'

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        if 'gene' in kwargs:
            self._genes = kwargs['gene'].split(',')
        else:
            self._genes = []

    def start_requests(self):
        if len(self._genes) == 0:
            # get all genes list
            url = 'http://deafnessvariationdatabase.org/api?&type=genelist&format=json'
            res = requests.get(url)
            for j in res.json():
                if 'gene' in j:
                    self._genes.append(j['gene'])
        # download from genes
        for gene in self._genes:
            yield Request(self.get_api_url({'type': 'gene', 'terms': gene, 'format': 'csv'}), dont_filter=True)
        return None

    def parse(self, response):
        res = response.body_as_unicode()
        head = ['_id', 'variation', 'gene', 'hgvs_protein_change', 'hgvs_nucleotide_change', 'variantlocale',
                'pathogenicity', 'disease', 'pubmed_id', 'dbsnp', 'summary_insilico', 'summary_frequency',
                'summary_published', 'comments', 'lrt_omega', 'phylop_score', 'phylop_pred', 'sift_score', 'sift_pred',
                'polyphen2_score', 'polyphen2_pred', 'lrt_score', 'lrt_pred', 'mutationtaster_score',
                'mutationtaster_pred', 'gerp_nr', 'gerp_rs', 'gerp_pred', 'evs_ea_ac', 'evs_ea_an', 'evs_ea_af',
                'evs_aa_ac', 'evs_aa_an', 'evs_aa_af', 'evs_all_ac', 'evs_all_an', 'evs_all_af', 'otoscope_aj_ac',
                'otoscope_aj_an', 'otoscope_aj_af', 'otoscope_co_ac', 'otoscope_co_an', 'otoscope_co_af',
                'otoscope_us_ac', 'otoscope_us_an', 'otoscope_us_af', 'otoscope_jp_ac', 'otoscope_jp_an',
                'otoscope_jp_af', 'otoscope_es_ac', 'otoscope_es_an', 'otoscope_es_af', 'otoscope_tr_ac',
                'otoscope_tr_an', 'otoscope_tr_af', 'otoscope_all_ac', 'otoscope_all_an', 'otoscope_all_af',
                'tg_afr_ac', 'tg_afr_an', 'tg_afr_af', 'tg_eur_ac', 'tg_eur_an', 'tg_eur_af', 'tg_amr_ac', 'tg_amr_an',
                'tg_amr_af', 'tg_eas_ac', 'tg_eas_an', 'tg_eas_af', 'tg_sas_ac', 'tg_sas_an', 'tg_sas_af', 'tg_all_ac',
                'tg_all_an', 'tg_all_af', 'exac_afr_ac', 'exac_afr_an', 'exac_afr_af', 'exac_amr_ac', 'exac_amr_an',
                'exac_amr_af', 'exac_eas_ac', 'exac_eas_an', 'exac_eas_af', 'exac_fin_ac', 'exac_fin_an', 'exac_fin_af',
                'exac_nfe_ac', 'exac_nfe_an', 'exac_nfe_af', 'exac_oth_ac', 'exac_oth_an', 'exac_oth_af', 'exac_sas_ac',
                'exac_sas_an', 'exac_sas_af', 'exac_all_ac', 'exac_all_an', 'exac_all_af']
        for line in res.split('\n'):
            line = line.strip()
            if not line or line[0] == '#':
                continue
            cols = line.split(',')
            data = [(head[i], cols[i]) for i in range(len(head)) if cols[i] != 'NULL']
            item = DeafnessItem(data)
            item['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            yield item
