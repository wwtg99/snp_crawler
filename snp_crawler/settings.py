# -*- coding: utf-8 -*-

# Scrapy settings for snp_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'snp_crawler'

SPIDER_MODULES = ['snp_crawler.spiders']
NEWSPIDER_MODULE = 'snp_crawler.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'snp_crawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'snp_crawler.middlewares.SnpCrawlerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'snp_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
#    'snp_crawler.pipelines.SnpCrawlerPipeline': 300,
    'snp_crawler.pipelines.MongodbPipeline': 300,
#    'snp_crawler.pipelines.ElasticsearchPipeline': 400
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# spider settings
SPIDER_SETTINGS = {
    'ensemble': {
        'query': {'genotypes': '0', 'phenotypes': '0', 'pops': '0', 'population_genotypes': '0'},
        'elasticsearch_fields': ['_id', 'name', 'ancestral_allele', 'minor_allele', 'synonyms', 'mappings', 'updated_at']
    },
    'dbsnp': {
        'query': {},
        'elasticsearch_fields': ['_id', 'name', 'gene', 'allele_origin', 'clinical_significance', 'updated_at']
    },
    'deafnessvdb': {
        'query': {},
        'elasticsearch_fields': ['_id', 'variation', 'gene', 'pathogenicity', 'dbsnp', 'updated_at']
    }
}

# pipeline settings
# mongodb
MONGO_URI = '192.168.0.21'
MONGO_DATABASE = 'testdb'
# MONGO_COLLECTION = 'test'  # default spider name

# elasticsearch
ELASTICSEARCH_HOST = 'http://192.168.0.21:9200'
ELASTICSEARCH_INDEX = ''  # default spider name
ELASTICSEARCH_INDEX_PREFIX = ''  # index prefix if ELASTICSEARCH_INDEX not provided
# ELASTICSEARCH_TYPE = 'test'  # default spider name
