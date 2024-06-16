from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time

options = webdriver.ChromeOptions()
options.add_argument("--proxy-server=http://localhost:8081")
driver = webdriver.Chrome(options=options)
driver.get("http://mitm.it")
time.sleep(1000)