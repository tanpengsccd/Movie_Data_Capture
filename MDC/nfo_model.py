# 用来存储nfo文件的模型
# https://kodi.wiki/view/NFO_files/Movies
from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel
# class NfoMovieParser(ABC):

#     @property
#     @abstractmethod
#     def website(self) -> str:
#         """ 具体影片详情地址 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def title(self) -> str:
#         """中文标题"""
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def originaltitle(self) -> str:
#         """原始标题"""
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def sorttitle(self) -> str:
#         """排序标题(如有则优先此标题排序,不实际显示;常用作集数或者系列排序)"""
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def customrating(self) -> str:
#         """ 用户评分 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def mpaa(self) -> str:
#         """ (国家)电影分级 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def year(self) -> str:
#         """ 年份 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def outline(self) -> str:
#         """ 简介(单行)"""
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def plot(self) -> str:
#         """ 简介(多行)"""
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def runtime(self) -> str:
#         """ 时长 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def poster(self) -> str:
#         """ 海报图 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def thumb(self) -> str:
#         """ 缩略图"""
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def cover(self) -> str:
#         """ 封面图 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def fanart(self) -> Fanart:
#         """ 背景图 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def actor(self) -> Actor:
#         """ 演员 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def studio(self) -> str:
#         """ 工作室 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def maker(self) -> str:
#         """ 制作商 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def num(self) -> str:
#         """ 番号 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def premiered(self) -> str:
#         """ 首映 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def releasedate(self) -> str:
#         """ 发行日期 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def release(self) -> str:
#         """ 发行日期 """
#         raise NotImplementedError

#     # ⬇️ 以下都是内部保留属性,媒体服务器不能识别这些字段,是用来存储下载地址的
#     @property
#     @abstractmethod
#     def url_poster(self) -> str:
#         """ 海报地址 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def url_thumb(self) -> str:
#         """ 缩略图地址 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def url_cover(self) -> str:
#         """ 封面图地址 """
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def url_fanart(self) -> Fanart:
#         """ 背景图地址 """
#         raise NotImplementedError


class NfoModel(BaseModel):

    class Movie(BaseModel):
        class Fanart(BaseModel):
            thumb: List[str]

        class Actor(BaseModel):
            name: str
        title: str
        """中文标题"""
        originaltitle: str
        """原始标题"""
        sorttitle: str = None
        """排序标题(如有则优先此标题排序,不实际显示;常用作集数或者系列排序)"""
        customrating: str
        """ 用户评分 """
        mpaa: str
        """ (国家)电影分级 """
        year: str
        """ 年份 """
        outline: str
        """ 简介(单行)"""
        plot: str
        """ 简介(多行)"""
        runtime: str
        """ 时长 """
        poster: str
        """ 海报图 """
        thumb: str
        """ 缩略图"""
        cover: str
        """ 封面图 """
        fanart: Fanart
        """ 背景图 """
        actor: Actor
        """ 演员 """
        studio: str
        """ 工作室 """
        maker: str
        """ 制作商 """
        num: str
        """ 番号 """
        premiered: str
        """ 首映 """
        releasedate: str
        """ 发行日期 """
        release: str
        """ 发行日期 """
        website: str
        """ 网站 """

        # ⬇️ 以下都是内部保留属性,媒体服务器不能识别这些字段,是用来存储下载地址的
        url_poster: str
        """ 海报地址 """
        url_thumb: str
        """ 缩略图地址 """
        url_cover: str
        """ 封面图地址 """
        url_fanart: Fanart
        """ 背景图地址 """

        # @property
        # def medias_to_download(self) -> list(str):
        #     """需要下载的媒体文件列表(含图)"""
        #     # * 用于解包 数组
        #     return [self.url_poster, self.url_thumb, self.url_cover, *self.url_fanart.thumb]

    movie: Movie
