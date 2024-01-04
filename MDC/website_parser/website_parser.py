# 参考 nfo_model 模型建立
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, TypeVar, Generic

from MDC.nfo_model import NfoModel



class WebsiteParser(ABC):
    """ 本意是使用抽象类来强制实现类必须实现对应 nfo属性key 的 xpath,但是 vscode 现在还无法强制提示未实现的属性或方法, 只有pycharm 可以强制提示
    """

    @property
    @abstractmethod
    def base_url(self) -> str:
        """ 站点baseUrl,有的站点可能会经常变化,需根据实际情况获取或修改 """
        raise NotImplementedError

    @property
    @abstractmethod
    def search_path(self) -> str:
        """ 搜索path 和base_url组合成完整的搜索地址 """
        raise NotImplementedError


    @property
    @abstractmethod
    def detail_html(self) -> str:
        """ 网页内容 """
        raise NotImplementedError
    
    @abstractmethod
    def Parser(self) -> NfoModel.Movie:
        """ 解析网页,返回NfoModel.Movie"""
        raise NotImplementedError


