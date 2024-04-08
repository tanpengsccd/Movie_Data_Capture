from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
PROXY = "127.0.0.1:6153"
options = Options()
options.add_argument(f'--proxy-server={PROXY}')
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get("https://www.pinterest.com/ideas/")

url = 'https://www.google.com/'
driver.get(url)
driver.maximize_window()
sleep(10)