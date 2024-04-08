from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import ddddocr
import platform
import os

# 获取当前项目路径（当前文件所在目录的上级目录）
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 获取当前工作路径
current_working_directory = os.getcwd()

logger.debug(f"当前项目路径: {project_path}")
logger.debug(f"当前工作路径: {current_working_directory}")


system = platform.system()
machine = platform.machine()
print("Operating System:", system)
print("Machine:", machine)


ocr = ddddocr.DdddOcr()
# export https_proxy=http://127.0.0.1:6152;export http_proxy=http://127.0.0.1:6152;export all_proxy=socks5://127.0.0.1:6153

# PROXY = "op.local:7890"  # 例: "127.0.0.1:8080"
PROXY = "127.0.0.1:6153"
chrome_options = Options()
chrome_options.add_argument(f'--proxy-server={PROXY}')
chrome_options.add_argument("--mute-audio")  # 将浏览器静音
# chrome_options.add_experimental_option("detach", True)  # 当程序结束时，浏览器不会关闭

# -----如果咋们的linux系统没有安装桌面，下面两句一定要有哦，必须开启无界面浏览器-------
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")

# chrome_options.binary_location='/Users/tanpengsccd/Downloads/chrome-mac-arm64/Google Chrome for Testing.app'

# ------------------------------------------------------------------------

# 如果是mac arm 环境下，chromedriver 路径 ./lib/chromedriver-mac-arm64/chromedriver
# 如果是linux x86_64 环境下，chromedriver 路径 ./lib/chromedriver-linux64/chromedriver
chromedriver_path_map = {
    "Darwin/arm64": "chromedriver-mac-arm64/chromedriver",
    "Linux/x86_64": "chromedriver-linux64/chromedriver"
}
executable_path = current_working_directory +'/MDC/lib/' + chromedriver_path_map[system + "/" + machine] 
if not executable_path:
    raise Exception("不支持的系统类型, 请自行下载对应版本的 chromedriver 并放到./lib 目录下。")

logger.debug(f"executable_path: {executable_path}")
# browser = webdriver.Chrome(options=chrome_options,
#                            executable_path=executable_path)
# 配置 header Cookie
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.pinterest.com/ideas/")

# browser.get("https://www.selenium.dev/selenium/web/web-form.html")
# title = browser.title
# assert title == "Web form"
browser.implicitly_wait(0.5)
browser.get("https://javdb.com/login")
# 登入 | JavDB 成人影片數據庫
assert 'JavDB' in browser.title
try:
    # 查找具有指定类名的图片元素
    image_element = browser.find_element_by_class_name("rucaptcha-image")

    # 获取图片的src属性，即图片的URL
    image_url = image_element.get_attribute("src")
    print("找到的图片URL:", image_url)
    with open("image_url", 'rb') as f:
        image = f.read()

        res = ocr.classification(image)
        print(res)
# 
except NoSuchElementException:
    print("没有找到具有指定类名的图片元素。")

print('不离鞘' in browser.page_source)

browser.quit()  # 关闭浏览器
