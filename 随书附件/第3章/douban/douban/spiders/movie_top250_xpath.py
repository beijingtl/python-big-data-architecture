"""
cd douban
scrapy crawl movie_top250_xpath -o movie_xpath.json
"""

import re

import unicodedata
from bs4 import BeautifulSoup
from scrapy.spiders import Spider

from ..items import DoubanItem


class MovieSpider(Spider):
    name = 'movie_top250_xpath'
    start_urls = [f'https://movie.douban.com/top250?start={i * 25}' for i in range(int(250 / 25))]

    def parse(self, response):
        movies = response.xpath('.//div[@class="item"]')
        for movie in movies:
            yield self.parse_movie(movie)

    # 转换/替换字符串
    @staticmethod
    def unicode_str(s):
        s_ = s.text if s is not None and not isinstance(s, str) else s
        return re.sub(r'\s{2,}|\n|主演: |导演: ', '', unicodedata.normalize('NFKC', s_)) if s_ else s_

    def parse_movie(self, movie):
        item = DoubanItem()
        item['title'] = self.unicode_str(movie.xpath('.//span[@class="title"]/text()').get())
        item['title_other'] = self.unicode_str(movie.xpath('.//span[@class="other"]/text()').get())
        p_info = BeautifulSoup(movie.xpath('.//p[@class=""]').get()).text.split('\n')
        p_info = [i for i in p_info if len(self.unicode_str(i)) > 2]
        if len(p_info[0].split('\xa0\xa0\xa0')) > 1:
            director, actors = p_info[0].split('\xa0\xa0\xa0')
        else:
            director = p_info[0]
            actors = None
        item['director'] = self.unicode_str(director)
        item['actors'] = self.unicode_str(actors)
        item['tags'] = self.unicode_str(p_info[1])
        item['avg_rate'] = float(movie.xpath('.//span[@class="rating_num"]/text()').get())
        item['voting_num'] = int(re.findall(r"\d+\.?\d*", movie.xpath('.//div[@class="star"]/span/text()')[-1].get())[0])
        item['quote'] = self.unicode_str(movie.xpath('.//p[@class="quote"]/span/text()').get())
        return item

