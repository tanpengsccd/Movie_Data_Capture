# Scrapy settings for MDCS project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "MDCS"

SPIDER_MODULES = ["MDCS.spiders"]
NEWSPIDER_MODULE = "MDCS.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "MDCS (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "MDCS.middlewares.MdcsSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "MDCS.middlewares.MdcsDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "MDCS.pipelines.MdcsPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# ❤️ 覆盖原参数

# 配置代理
HTTP_PROXY = 'http://127.0.0.1:6152'

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Host": "javdb.com",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "macOS",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    # "Accept-Encoding": "gzip, deflate, br, zstd", #开了会乱码 scrapy 似乎不能自动处理 gzip解压缩
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,ja;q=0.5",
    "Cookie": "list_mode=h; theme=auto; locale=zh; over18=1; _jdb_session=pnpzddALy%2FrzA%2BN5J%2B7O%2BkN%2F%2FKmA4U52hZByeoEgFBfpcg8gKE1SloJVJXLVbBDphneUtYooreqsiZvHpA5mCro0l5xmnbPeMeFRXBjCqYkBT2NXwPG4HWcYYgaaBN0wAbfGecRo1awfTo%2FBSQ8NbLTGa28ouGY0i%2Fu%2FnLloWAW%2BDaga%2FTCEDtM1PEbzCAMBOJIBgd6ewRTHv%2F6GX2%2Bby2jnkNrvYvZRiE5WK44xPieXhP%2FF%2FEEiwvUM0nlXz58HNaUTIkYfg4avqhW6kAR1I9eVSbdenWw0EtQve5Wp2dhdY5nfsTEkZLMp--P4Yc19OU1%2FlIX6%2Ft--d%2B8YSusPAVqiPrvvmDNNdw%3D%3D; cf_clearance=tO7VcHnnM1IVMhVysN6hZnkhikWE7skPzcuKyZl3BzA-1719484800-1.0.1.1-MKZjrFb5UH2ILgvkiQn_ixuRV1gim95P7zGtXBLLISQGA4lTb0yrCwVUuuOpSI_7dqwim6.8m1SaoaenfIzXtQ",

}  # 添加或修改 User-Agent 头
