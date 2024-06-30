# global_config.py
from typing import List
from pydantic import BaseModel, ValidationInfo, field_validator

from enum import Enum
import yaml
from helper.loguru_config import logu, Now

# ---------------------------------定义的配置模型 ------------


class ConfigModel(BaseModel):
    class IndexConfig(BaseModel):
        """索引模式配置
        """
        is_disabled: bool = False
        # class Main_Mode(str, Enum):
        #     """运行模式
        #     """
        #     Indexing = 'indexing'
        #     """只读取目标文件夹下的视频文件,存入数据库,不做任何其他操作"""
        #     Scraping = 'scraping'
        #     Organizing = 'organizing'
        #     ScrapingInAnalysisFolder = 'scrapingInAnalysisFolder'

        # main_mode: Main_Mode = Main_Mode.Indexing

        # 数据源目录:1. 目录下必须含有视频文件 2.视频文件文件路径必须有有番号或者电影名  例如:该文件夹有文件‘ABP-001/a.mp4’:合法 ,该文件夹有文件'a.mp4': 不合法.
        source_dir: str = './'
        # 元文件目录: 刮削产生的素材文件存在此(不含nfo),如封面图片
        metadata_dir: str = './metadata'
        # 忽略路径:
        ignore_dirs: List[str] = ['.git', '.idea', '.vscode', 'node_modules', 'dist', 'build', 'docs', 'logs', 'tmp']
        # 数据库 uri 如 mysql://avnadmin:AVNS_XXXX@aiven-leonardosccd-ec6b.j.aivencloud.com:27840/defaultdb?ssl-mode=REQUIRED
        database_uri: str = None

        # 定制main_mode 字段 的验证器(解析器) , mode 默认是after 意思先按照 类型 解析,然后才会进这个 自定义的验证器
        # @field_validator('main_mode', mode='before')
        # @classmethod
        # def main_mode_valid(cls, v: str, info: ValidationInfo) -> Main_Mode:
        #     #  兼容 大小写, 必须在 之前解析所以用mode='before'
        #     if isinstance(v, str):
        #         v_lower = v.lower()
        #         # 尝试精确匹配(忽略大小写)
        #         match = next((mode for mode in cls.Main_Mode if mode.value == v_lower), None)
        #         if match:
        #             return match
        #         # 尝试起始字符匹配
        #         match = next((mode for mode in cls.Main_Mode if mode.value.startswith(v_lower)), None)
        #         if match:
        #             return match
        #         raise ValueError('main_mode must be ' + ' or '.join([f'"{e.value}"' for e in cls.Main_Mode]))
        #     else:
        #         raise ValueError('main_mode must be ' + ' or '.join([f'"{e.value}"' for e in cls.Main_Mode]))

    class Scrape(BaseModel):
        """ 刮削模式配置 """
        class JavdbConfig(BaseModel):
            cookies: dict = {}

            @field_validator('cookies', mode='before')
            @classmethod
            def parse_cookie(cls, cookie_str: str):
                """解析cookie字符串"""
                cookie_dict = {}
                for item in cookie_str.split(';'):
                    key, value = item.split('=')
                    # 去除空格
                    cookie_dict[key.strip()] = value.strip()
                return cookie_dict
        is_disabled: bool = False
        metadata_dir: str = "./metadata_dir"
        javdb: JavdbConfig

    class Organize(BaseModel):
        """整理模式配置"""
        is_disabled: bool = False
        mode: str = 'direct'
        """ 模式
        direct:  素材(nfo,封面图)直接移动到影片同级路径
        """
    index: IndexConfig
    scrape: Scrape

# --------------------------------以上是定义模型------------------------------


def load_yaml_config(file_path: str) -> ConfigModel:
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
    return ConfigModel(**yaml_data)


def save_config(config_data):
    with open('config.yml', 'w') as file:
        yaml.dump(config_data, file)


LOGGER = logu(__name__)
# _loaded_config = load_config()
# _default_config = {
#     # 数据源目录:1. 目录下必须含有视频文件 2.视频文件文件路径必须有有番号或者电影名  例如:该文件夹有文件‘ABP-001/a.mp4’:合法 ,该文件夹有文件'a.mp4': 不合法.
#     'source_dir': './',
#     # 元文件目录: 刮削产生的素材文件存在此(不含nfo),如封面图片
#     'metadata_dir': './metadata',
#     # 忽略路径:
#     'ignore_dir': ['.git', '.idea', '.vscode', 'node_modules', 'dist', 'build', 'docs', 'logs', 'tmp'],
#     # 数据库 uri 如 mysql://avnadmin:AVNS_XXXX@aiven-leonardosccd-ec6b.j.aivencloud.com:27840/defaultdb?ssl-mode=REQUIRED
#     'database_uri': None,
# }
config = load_yaml_config('config.yml')
LOGGER.info(f'config loaded: {config}')
