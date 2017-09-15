# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SnpCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class EnsembleVariationItem(scrapy.Item):
    _id = scrapy.Field()  # used for mongodb
    _searchable = scrapy.Field()  # used for elasticsearch
    name = scrapy.Field()
    MAF = scrapy.Field()
    source = scrapy.Field()
    ancestral_allele = scrapy.Field()
    minor_allele = scrapy.Field()
    ambiguity = scrapy.Field()
    mappings = scrapy.Field()
    clinical_significance = scrapy.Field()
    var_class = scrapy.Field()
    synonyms = scrapy.Field()
    evidence = scrapy.Field()
    most_severe_consequence = scrapy.Field()
    phenotypes = scrapy.Field()
    genotypes = scrapy.Field()
    populations = scrapy.Field()
    population_genotypes = scrapy.Field()
    updated_at = scrapy.Field()
