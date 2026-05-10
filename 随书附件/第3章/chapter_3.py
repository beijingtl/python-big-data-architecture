"""
第3章程序示例
"""

# 3.6 使用Requests抓取豆瓣电影数据并保存到sqlite

# 3.6.2 基本示例
import requests

r = requests.get('https://httpbin.org/get')
print(r.text)
print(r.status_code)
print(r.reason)
print(r.headers)
r.close()

# 3.6.3 高级用法
import re
import time
import unicodedata
import sqlite3
from contextlib import closing
from bs4 import BeautifulSoup

# 获取数据
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"}
html_raws = []
for i in range(int(250 / 25)):
    with requests.get(f'https://movie.douban.com/top250?start={i * 25}', headers=headers, verify=False) as r:
        # 获取数据
        html_raws.append(r.text)
        time.sleep(1)


# 转换/替换字符串
def unicode_str(s):
    s_ = s.text if s is not None and not isinstance(s, str) else s
    return re.sub(r'\s{2,}|\n|主演: |导演: ', '', unicodedata.normalize('NFKC', s_)) if s_ else s_


# 解析数据
def parse_movie(movie):
    title = movie.find(name='span', attrs={'class': 'title'})
    title_other = movie.find(name='span', attrs={'class': 'other'})
    p_info = movie.find(name='p', attrs={'class': ''}).text.split('\n')
    p_info = [i for i in p_info if len(unicode_str(i)) > 2]
    if len(p_info[0].split('\xa0\xa0\xa0')) > 1:
        director, actors = p_info[0].split('\xa0\xa0\xa0')
    else:
        director = p_info[0]
        actors = None
    tags = p_info[1]
    avg_rate = float(movie.find(name='span', attrs={'class': 'rating_num'}).text)
    voting_num = int(re.findall(r"\d+\.?\d*", movie.find_all(name='span', attrs={'class': ''})[-1].text)[0])
    quote = movie.find(name='p', attrs={'class': 'quote'})
    return unicode_str(title), unicode_str(title_other), unicode_str(director), unicode_str(actors), unicode_str(
        tags), avg_rate, voting_num, unicode_str(quote)


# 核心解析过程
html_parse = []
for html_raw in html_raws:
    soup = BeautifulSoup(html_raw, 'lxml')
    movies = soup.find_all(name='div', attrs={'class': 'item'})
    for movie in movies:
        html_parse.append(parse_movie(movie))

# 将数据写库
with sqlite3.connect('douban.db') as conn:
    with closing(conn.cursor()) as cur:
        # 删除旧表
        # cur.execute('DROP TABLE IF EXISTS movie')
        # conn.commit()
        # 创建新表
        sql = """CREATE TABLE
                 IF NOT EXISTS movie(
                    tile TEXT,
                    title_other TEXT,
                    director TEXT,
                    actors TEXT,
                    tags TEXT,
                    avg_rate FLOAT,
                    voting_num INTEGER,
                    quote TEXT
        )"""
        cur.execute(sql)
        conn.commit()
        # 批量写入数据
        cur.executemany('INSERT INTO movie VALUES (?,?,?,?,?,?,?,?)', html_parse)
        conn.commit()

        # 查询验证数据
        cur.execute("select count(*) from movie")
        print(cur.fetchone())
        cur.execute("select * from movie")
        print(cur.fetchone())

# 3.7 使用scrapy抓取数据并保存到MongoDB
# 具体见 douban 目录下的程序文件
