
# javdb.py
import re
import scrapy
from helper.loguru_config import logu
from helper.global_config import config
#

# 笔记📒 可单独 执行 该 spider :  scrapy crawl javdb -O javdb.json


class JavdbSpider(scrapy.Spider):

    name = "javdb"
    start_urls = ['https://javdb.com/v/Yn4bz']

    def __init__(self, start_url=None, *args, **kwargs):
        super(JavdbSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else ['https://javdb.com/v/Yn4bz']
    # 定制 start_requests 方法,同名key优先级会高于setting.py里的配置.
    # 注入cookies

    def start_requests(self):
        # 必须是中文(只有繁体) 才能匹配到电影数据
        headers = {
            "Host": "javdb.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "macOS",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            # "Accept-Encoding": "gzip, deflate, br, zstd", #开了会乱码 scrapy 似乎不能自动处理 gzip解压缩
            "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.6,ja;q=0.5,en-US;q=0.8,en;q=0.7",

        }
        _default_cookies = {'locale': 'zh', }
        cookies = {**config.javdb.cookies, **_default_cookies}
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, cookies=cookies, callback=self.parse)

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
