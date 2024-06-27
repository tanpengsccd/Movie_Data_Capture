# global_config.py
import yaml
from helper.loguru_config import logu, Now


def load_config():
    with open('config.yml', 'r') as file:
        return yaml.safe_load(file)


def save_config(config_data):
    with open('config.yaml', 'w') as file:
        yaml.dump(config_data, file)


LOGGER = logu(__name__)
_loaded_config = load_config()
_default_config = {
    # 数据源目录:1. 目录下必须含有视频文件 2.视频文件文件路径必须有有番号或者电影名  例如:该文件夹有文件‘ABP-001/a.mp4’:合法 ,该文件夹有文件'a.mp4': 不合法.
    'source_dir': './',
    # 元文件目录: 刮削产生的素材文件存在此(不含nfo),如封面图片
    'metadata_dir': './metadata',
    # 忽略路径:
    'ignore_dir': ['.git', '.idea', '.vscode', 'node_modules', 'dist', 'build', 'docs', 'logs', 'tmp'],
    # 数据库 uri 如 mysql://avnadmin:AVNS_XXXX@aiven-leonardosccd-ec6b.j.aivencloud.com:27840/defaultdb?ssl-mode=REQUIRED
    'database_uri': None,
}
config = {**_default_config, **{k: v for k, v in _loaded_config.items() if v is not None}}
LOGGER.info(f'config loaded: {config}')
