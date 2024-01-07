# 使用avsox 站点
from lxml import html
import requests
from MDC.website_parser.website_parser import WebsiteParser


class Avsox(WebsiteParser):

    def _get_available_site_base_url(self, number: str) -> str:
        """ 获取可用的站点地址 """
        # 访问 https://tellme.pw/avsox 获取最新网址
        # 获取HTML内容
        url = "https://tellme.pw/avsox"
        response = requests.get(url)
        tree = html.fromstring(response.content)
        # 使用XPath获取数据
        links = tree.xpath('//div[@class="container"]/div/a/@href')
        return links[0] if links else ''

    base_url = _get_available_site_base_url()  # 'https://avsox.click'

    def search_number(self, number: str) -> [str]:
        """ 搜索番号,返回网页链接列表 """
        url = self.base_url + '/cn/search/' + number
        response = requests.get(url)
        tree = html.fromstring(response.content)
        # 使用XPath获取数据
        links = tree.xpath('//*[@id="waterfall"]/div/a/@href')
        return [self.base_url + link for link in links]

    @property
    @abstractmethod
    def detail_html(self) -> str:
        """ 网页内容 """
        raise NotImplementedError

    @abstractmethod
    def Parser(self) -> NfoModel.Movie:
        """ 解析网页,返回NfoModel.Movie"""
        raise NotImplementedError
