from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import ddddocr

ocr = ddddocr.DdddOcr()


PROXY = "op.local:7890"  # 例: "127.0.0.1:8080"
chrome_options = Options()
chrome_options.add_argument("--mute-audio")  # 将浏览器静音
# chrome_options.add_experimental_option("detach", True)  # 当程序结束时，浏览器不会关闭

# -----如果咋们的linux系统没有安装桌面，下面两句一定要有哦，必须开启无界面浏览器-------
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f'--proxy-server={PROXY}')

# ------------------------------------------------------------------------


browser = webdriver.Chrome(options=chrome_options,
                           executable_path='./chromedriver-linux64/chromedriver')
# 配置 header Cookie


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

except NoSuchElementException:
    print("没有找到具有指定类名的图片元素。")

print('不离鞘' in browser.page_source)

browser.quit()  # 关闭浏览器
