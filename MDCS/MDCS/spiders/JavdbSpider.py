
# javdb.py
import re
import scrapy
from helper.loguru_config import logu

#

# 笔记📒 可单独 执行 该 spider :  scrapy crawl javdb -O javdb.json


class JavdbSpider(scrapy.Spider):

    name = "javdb"
    start_urls = ['https://javdb.com/v/Yn4bz']

    def __init__(self, start_url=None, *args, **kwargs):
        super(JavdbSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else ['https://javdb.com/v/Yn4bz']

    def parse(self, response):
        LOGGER = logu(__name__)
        # 这一块是详情
        detail_content = response.css('div.video-detail')
        # SSNI-549
        # code = detail.css('strong::text').get() # css选择器 简单,但是不如xpath灵活功能丰富
        # '絶頂してピクピクしているおま●こを容赦なく突きまくる怒涛のおかわり激ピストン性交 星宮一花 '
        title = detail_content.css('strong.current-title::text').get()  # css选择器

        movie_code_series = detail_content.xpath('//div[contains(strong/text(), "番號")]/span[@class="value"]/a/text()').get('')  # 可能空
        movie_number = response.xpath('//div[contains(@class, "panel-block") and contains(strong/text(), "番號")]/span[@class="value"]/text()').get()
        # 番号
        code = movie_code_series + movie_number
        # 番号系列URL
        movie_code_series_url_path = detail_content.xpath('//div[contains(strong/text(), "番號")]/span[@class="value"]/a/@href').get()  # 如 /video_codes/ABP
        # 发行日期
        release_date = detail_content.xpath('//div[contains(strong/text(), "日期:")]/span[@class="value"]/text()').get()  # '2017-01-27'
        # 時長
        duration = detail_content.xpath('//div[contains(strong/text(), "時長:")]/span[@class="value"]/text()').get()  # '120分鐘'
        # 導演
        director = detail_content.xpath('//div[contains(strong/text(), "導演:")]/span[@class="value"]/a/text()').get()
        # 片商
        maker = detail_content.xpath('//div[contains(strong/text(), "片商:")]/span[@class="value"]/a/text()').get()
        # 發行
        publisher = detail_content.xpath('//div[contains(strong/text(), "發行:")]/span[@class="value"]/a/text()').get()
        # 系列:
        series = detail_content.xpath('//div[contains(strong/text(), "系列:")]/span[@class="value"]/a/text()').get()
        # 評分: 5分制
        _ratingContent = detail_content.xpath('//div[contains(strong/text(), "評分:")]/span[@class="value"]/text()').get()
        rating = re.search(r'(?<=\xa0)(.+)(?=分)', _ratingContent)
        # 類別:
        tags = detail_content.xpath('//div[contains(strong/text(), "類別:")]/span[@class="value"]/a/text()').getall()  # ['拘束', '單體作品','玩具']
        # 演員:
        # ['松永さな', '森林原人', '佐川銀次', 'セツネヒデユキ', '南佳也', '岩沢', 'ザーメン二郎', 'イェーイ高島']
        actors = detail_content.xpath('//div[contains(strong/text(), "演員:")]/span[@class="value"]/a/text()').getall()

        # 磁力链接
        magnet_links = response.xpath('//div[@id="magnets-content"]/div[contains(@class,"item")]/div[contains(@class,"buttons")]/button/@data-clipboard-text').getall()

        #  封面URL
        cover_url = response.xpath('//a[@class="cover-container"]/img/@src').get()
        # 预览图URL(样本图)
        preview_image_urls = response.xpath('//div[@class="tile-images preview-images"]/a/@href').getall()
        # 排名标签 TOP250
        # ranking_tags = response.xpath('//div[@class="control ranking-tags"]/a/span/text()').getall()
        # 首先获取所有的 div 元素
        _ranking_tags_doms = response.xpath('//div[@class="control ranking-tags"]/a[@class="tags has-addons"]')
        # 对于每个 div 元素，获取其内部的 a 标签的文本 : [['No.79', 'JavDB 影片TOP250'], ['No.69', 'JavDB 有碼影片TOP250'], ['No.2', 'JavDB 2017年度TOP250']]
        ranking_tags = [div.xpath('.//span/text()').getall() for div in _ranking_tags_doms]

        LOGGER.info(title, movie_code_series, movie_number)
        return {
            'title': title,
            'code': code,
            'movie_code_series': movie_code_series,
            'movie_number': movie_number,
            'movie_code_series_url_path': movie_code_series_url_path,
            'release_date': release_date,
            'duration': duration,
            'director': director,
            'maker': maker,
            'publisher': publisher,
            'series': series,
            'rating': rating.group(1) if rating else None,
            'tags': tags,
            'actors': actors,
            'magnet_links': magnet_links,
            'cover_url': cover_url,
            'preview_image_urls': preview_image_urls,
            'ranking_tags': ranking_tags,
        }
        # yield {
        #     'title': title,
        #     'code': code,
        #     # 'movie_code_series': movie_code_series,
        #     # 'movie_number': movie_number,
        #     # 'movie_code_series_url_path': movie_code_series_url_path,
        #     # 'release_date': release_date,
        #     # 'duration': duration,
        #     # 'director': director,
        #     # 'maker': maker,
        #     # 'publisher': publisher,
        #     # 'series': series,
        #     # 'rating': rating.group(1) if rating else None,
        #     # 'tags': tags,
        #     # 'actors': actors,
        #     # 'magnet_links': magnet_links,
        #     # 'cover_url': cover_url,
        #     # 'preview_image_urls': preview_image_urls,
        #     # 'ranking_tags': ranking_tags,
        # }
