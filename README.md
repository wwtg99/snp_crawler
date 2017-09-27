SNP Crawler
===========

Crawler SNP data from web services.

# Dependency
- Python 3.5+ (not tested in Python 2.7)
- Scrapy

# Usage
```
# show all spiders
scrapy list

# run ensemble
scrapy crawl ensemble -a rs=rs7412,rs6379

# load from file (use glob to support wildcard)
scrapy crawl ensemble -a file=../data/rs.txt

# load from bed file (use glob to support wildcard)
scrapy crawl ensemble -a bed=../data/bed_chr_MT.bed

# load from vcf file (use glob to support wildcard)
scrapy crawl ensemble -a vcf=../data/*.vcf
```

# Supported spiders
- Ensemble
- dbSNP

# Supported data targets
- MongoDB: for whole data
- Elasticsearch: for fields to search
