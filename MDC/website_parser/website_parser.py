# 参考 nfo_model 模型建立
from abc import ABC, abstractmethod


class WebsiteParser(ABC):
    # class XpathExpressions:
    # @property
    # @abstractmethod
    # def xpath_expressions(self) -> :
    @property
    @abstractmethod
    def target_url(self) -> str:
        """ 目标网址 """
        raise NotImplementedError

    @property
    @abstractmethod
    def title(self) -> str:
        """中文标题"""
        raise NotImplementedError

    @property
    @abstractmethod
    def originaltitle(self) -> str:
        """原始标题"""
        raise NotImplementedError

    @property
    @abstractmethod
    def sorttitle(self) -> str:
        """排序标题(如有则优先此标题排序,不实际显示;常用作集数或者系列排序)"""
        raise NotImplementedError

    @property
    @abstractmethod
    def customrating(self) -> str:
        """ 用户评分 """
        raise NotImplementedError

    @property
    @abstractmethod
    def mpaa(self) -> str:
        """ (国家)电影分级 """
        raise NotImplementedError

    @property
    @abstractmethod
    def year(self) -> str:
        """ 年份 """
        raise NotImplementedError

    @property
    @abstractmethod
    def outline(self) -> str:
        """ 简介(单行)"""
        raise NotImplementedError

    @property
    @abstractmethod
    def plot(self) -> str:
        """ 简介(多行)"""
        raise NotImplementedError

    @property
    @abstractmethod
    def runtime(self) -> str:
        """ 时长 """
        raise NotImplementedError

    @property
    @abstractmethod
    def poster(self) -> str:
        """ 海报图 """
        raise NotImplementedError

    @property
    @abstractmethod
    def thumb(self) -> str:
        """ 缩略图"""
        raise NotImplementedError

    @property
    @abstractmethod
    def cover(self) -> str:
        """ 封面图 """
        raise NotImplementedError

    @property
    @abstractmethod
    def fanart(self) -> Fanart:
        """ 背景图 """
        raise NotImplementedError

    @property
    @abstractmethod
    def actor(self) -> Actor:
        """ 演员 """
        raise NotImplementedError

    @property
    @abstractmethod
    def studio(self) -> str:
        """ 工作室 """
        raise NotImplementedError

    @property
    @abstractmethod
    def maker(self) -> str:
        """ 制作商 """
        raise NotImplementedError

    @property
    @abstractmethod
    def num(self) -> str:
        """ 番号 """
        raise NotImplementedError

    @property
    @abstractmethod
    def premiered(self) -> str:
        """ 首映 """
        raise NotImplementedError

    @property
    @abstractmethod
    def releasedate(self) -> str:
        """ 发行日期 """
        raise NotImplementedError

    @property
    @abstractmethod
    def release(self) -> str:
        """ 发行日期 """
        raise NotImplementedError

    @property
    @abstractmethod
    def website(self) -> str:
        """ 网站 """
        raise NotImplementedError

    # ⬇️ 以下都是内部保留属性,媒体服务器不能识别这些字段,是用来存储下载地址的
    @property
    @abstractmethod
    def url_poster(self) -> str:
        """ 海报地址 """
        raise NotImplementedError

    @property
    @abstractmethod
    def url_thumb(self) -> str:
        """ 缩略图地址 """
        raise NotImplementedError

    @property
    @abstractmethod
    def url_cover(self) -> str:
        """ 封面图地址 """
        raise NotImplementedError

    @property
    @abstractmethod
    def url_fanart(self) -> Fanart:
        """ 背景图地址 """
        raise NotImplementedError


class Avsox(WebsiteParser):

    @property
    def target_url(self) -> str:
        return ''
