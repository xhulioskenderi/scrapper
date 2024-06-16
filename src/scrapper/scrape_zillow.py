from browser_setup_code import Chrome, Mozilla
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

driver = Chrome(remote=True)
final_driver = driver.get_driver()


class ScrapeRealEstate():
    def __init__(self):
        self.html_content = ''

    def zillow(self):
        #final_driver.get('https://www.realtor.com/realestateandhomes-search/Los-Angeles_CA')
        final_driver.get('https://www.google.com')
        final_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        time.sleep(2)
        # Find the ul element by class name
        self.html_content = final_driver.page_source
        print(self.html_content)
        final_driver.quit()


real = ScrapeRealEstate()
real.zillow()

