# 用来存储nfo文件的模型
# https://kodi.wiki/view/NFO_files/Movies
from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

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
