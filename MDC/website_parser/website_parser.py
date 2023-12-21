
from abc import ABC, abstractmethod


class WebsiteParser(ABC):

    @abstractmethod
    def target_url(self) -> str:
        """ 目标网址 """
        # raise NotImplementedError
        # pass


class Avsox(WebsiteParser):
    def a(self) -> str:
        return 'a'
