# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import mysql.connector
from itemadapter import ItemAdapter


class MdcsPipeline:
    def process_item(self, item, spider):
        return item


class MySQLPipeline(object):
    def open_spider(self, spider):
        # 在爬虫启动时创建数据库连接
        self.connection = mysql.connector.connect(
            host='your_host',  # 通常是 localhost 或 IP 地址
            user='your_user',
            password='your_password',
            database='your_database'
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        # 关闭游标和连接
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        # 编写 SQL 语句插入数据
        insert_query = """
        INSERT INTO movies (title, code, url)
        VALUES (%s, %s, %s)
        """
        self.cursor.execute(insert_query, (
            item['title'],
            item['code'],
            item['url']
        ))
        self.connection.commit()
        return item
