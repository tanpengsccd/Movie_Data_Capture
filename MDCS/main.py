from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from MDCS.spiders.JavdbSpider import JavdbSpider  # 确保正确导入你的 Spider 类
from helper.loguru_config import logu
from helper.global_config import config
from index import __main__ as index_main


def main():
    LOGGER = logu(__name__)
    LOGGER.info(f'MDCS开始运行')
    # TODO 读取配置 再设置完配置后 保存配置
    LOGGER.info(config.scrape.javdb.cookies)

    # index: 只读操作,  读取文件列表 , 遍历列表的路径 , 提取番号,存入 数据库(sqlite/mysql5.7)

    index_main.main()  # 以后考虑作为 subprocess 独立运行

    # scrape 刮削: 写, 查询编号 ,提取页面信息nfo, 下载metadata(图片)
    # organize 整理: 删,写,按演员分类/按系列分类,封面添加 tag

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
