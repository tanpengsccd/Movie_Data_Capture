from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from MDCS.spiders.JavdbSpider import JavdbSpider  # 确保正确导入你的 Spider 类
from helper.loguru_config import logu, Now
from helper.global_config import config


def main():

    LOGGER = logu(__name__)
    LOGGER.info(f'开始运行')
    # TODO 读取配置 再设置完配置后 保存配置
    LOGGER.info(config['source_dir'])
    # 读取文件列表
    # 遍历列表的路径
    # 1. 提取番号
    # 2. 查询番号
    # 3. # 提取页面信息
    # settings = get_project_settings()
    # for k in sorted(settings.keys()):
    #     print(f'{k}: {settings[k]}')
    process = CrawlerProcess(get_project_settings())
    process.crawl(JavdbSpider, start_url='https://javdb.com/v/Aq5nO')
    process.start()

    # javdb_data =
    # 4. 保存至数据库

    LOGGER.info(f'运行结束')


if __name__ == '__main__':
    main()
