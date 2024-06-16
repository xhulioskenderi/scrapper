from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.chrome import ChromeDriverManager
import time



class mozilla:

    def __init__(self, randomizeWidth, randomizeHeight) -> None:
        self.randomizeWidth = randomizeWidth
        self.randomizeHeight = randomizeHeight
        self.profile = FirefoxProfile('/Users/xhulioskenderi/Desktop/CryptoP/openai-quickstart-python/scrapper/mozilla_profiles/Profiles/7wvk58qd.Moziila3')
        self.options = Options()
        self.options.profile = self.profile
        self.options.set_preference("general.useragent.override","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
        self.options.set_preference("dom.webnotifications.serviceworker.enabled", False)
        self.options.set_preference("dom.webnotifications.enabled", False)
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.service = FirefoxService("/Users/xhulioskenderi/Desktop/CryptoP/openai-quickstart-python/scrapper/tests/geckodriver")
        self.driver = webdriver.Firefox(service=self.service, options=self.options)
        self.driver.set_window_size(randomizeWidth, randomizeHeight)
            



class chrome:

    def __init__(self, randomizeSize) -> None:
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


#class safari:

browser = mozilla(1024, 768)
browser.driver.get("https://www.whatismybrowser.com/detect/what-is-my-user-agent/")
time.sleep(10000)
