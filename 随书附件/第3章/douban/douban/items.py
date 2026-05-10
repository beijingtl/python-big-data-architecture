# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class DoubanItem(scrapy.Item):
    title = scrapy.Field()
    title_other = scrapy.Field()
    director = scrapy.Field()
    actors = scrapy.Field()
    tags = scrapy.Field()
    avg_rate = scrapy.Field()
    voting_num = scrapy.Field()
    quote = scrapy.Field()


