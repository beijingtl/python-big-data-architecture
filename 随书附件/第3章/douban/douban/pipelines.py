# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
from contextlib import closing
from pymongo import MongoClient


class SqliteWriterPipeline(object):

    def insert(self, items):
        with sqlite3.connect('douban.db') as conn:
            with closing(conn.cursor()) as cur:
                # 创建新表
                sql = """CREATE TABLE
                         IF NOT EXISTS movie_scrapy(
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
                cur.executemany('INSERT INTO movie_scrapy VALUES (?,?,?,?,?,?,?,?)', items)
                conn.commit()

                # 查询验证数据
                # cur.execute("select count(*) from movie_scrapy")
                # print(cur.fetchone())
                # cur.execute("select * from movie_scrapy")
                # print(cur.fetchone())
                # 查询所有表
                # cur.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
                # print(cur.fetchall())

    def process_item(self, item, spider):
        names = ['title', 'title_other', 'director', 'actors', 'tags', 'avg_rate', 'voting_num', 'quote']
        items = [[item[i] for i in names]]  # 保证顺序统一
        self.insert(items)
        return item


class MongoDBWriterPipeline(object):

    def insert(self, items):
        with MongoClient('192.168.0.54', 27017) as client:
            db = client['douban']
            collection = db['movie']
            collection.insert_many(items)

        # for i in collection.find():
        #     print(i)

    def process_item(self, item, spider):
        self.insert([dict(item)])
        return item