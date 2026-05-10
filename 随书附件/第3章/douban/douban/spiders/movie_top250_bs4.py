"""
cd douban
scrapy crawl movie_top250_bs4 -o movie_bs4.json
"""

import re

import unicodedata
from bs4 import BeautifulSoup
from scrapy.spiders import Spider

from ..items import DoubanItem


class MovieSpider(Spider):
    name = 'movie_top250_bs4'
    start_urls = [f'https://movie.douban.com/top250?start={i * 25}' for i in range(int(250 / 25))]

    def parse(self, response):
        movies = BeautifulSoup(response.body, 'lxml').find_all(name='div', attrs={'class': 'item'})
        for movie in movies:
            yield self.parse_movie(movie)

    # 转换/替换字符串
    @staticmethod
    def unicode_str(s):
        s_ = s.text if s is not None and not isinstance(s, str) else s
        return re.sub(r'\s{2,}|\n|主演: |导演: ', '', unicodedata.normalize('NFKC', s_)) if s_ else s_

    def parse_movie(self, movie):
        item = DoubanItem()
        item['title'] = self.unicode_str(movie.find(name='span', attrs={'class': 'title'}))
        item['title_other'] = self.unicode_str(movie.find(name='span', attrs={'class': 'other'}))
        p_info = movie.find(name='p', attrs={'class': ''}).text.split('\n')
        p_info = [i for i in p_info if len(self.unicode_str(i)) > 2]
        if len(p_info[0].split('\xa0\xa0\xa0')) > 1:
            director, actors = p_info[0].split('\xa0\xa0\xa0')
        else:
            director = p_info[0]
            actors = None
        item['director'] = self.unicode_str(director)
        item['actors'] = self.unicode_str(actors)
        item['tags'] = self.unicode_str(p_info[1])
        item['avg_rate'] = float(movie.find(name='span', attrs={'class': 'rating_num'}).text)
        item['voting_num'] = int(re.findall(r"\d+\.?\d*", movie.find_all(name='span', attrs={'class': ''})[-1].text)[0])
        item['quote'] = self.unicode_str(movie.find(name='p', attrs={'class': 'quote'}))
        return item
