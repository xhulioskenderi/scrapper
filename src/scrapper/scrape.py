import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from webdriver_manager.firefox import GeckoDriverManager

#Put them inside a function
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
safariDriver = webdriver.Safari

#Implement it so the input comes from elsewhere


'''        
self.mozillaUserAgent = webdriver.FirefoxOptions()
self.mozillaDriver = webdriver.Firefox(FirefoxDriverManager().install(), firefox_options=firefox_options)
self.operaUserAgent = webdriver.OperaOptions()
'''

def randomizeResolution():
    resList = [(1920,1080), (1366,768), (1440,900), (1536,864), (2560,1440), (1680,1050), (1280,720), (1280,800), (1792,1120), (1600,900)]
    pickResolution = resList[random.randint(0, len(resList)-1)]
    strResolution = str(pickResolution)
    finalResolution = "--window-size="
    for element in strResolution:
        if element == "(" or element == ")":
            pass
        else:
            finalResolution = finalResolution + element
    return finalResolution

def randomizeUserAgent():
    userAgentPool = []


def scrapeFirstPage(query: str):
    links = [] # Initiate empty list to capture final results
    # Specify number of pages on google search, each page contains 10 #links
    n_pages = 2
    for page in range(1, n_pages):
        url = "http://www.google.com/search?q=" + query + "&start=" +      str((page - 1) * 10)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # soup = BeautifulSoup(r.text, 'html.parser')
        search = soup.find_all('div', class_="yuRUbf")
        for h in search:
            links.append(h.a.get('href'))
    return links

def scrapeAllThings(links):
    websites = scrapeFirstPage(links)


def answerUserQuery():
    #Handle user requests from the front end
    return None
"""
    for element in links:
        driver.get(element)
        soup_1 = BeautifulSoup(driver.page_source, 'html.parser')
        print(soup_1)
        print("=============================================================================              ")
    #for i in links:
        #driver.get(i)
     #   print(i)
    #sort the problem of the objects
    #get the html from the links
"""

scrapeFirstPage("gym workout program")
'''
def parseHtml(html):
    search = soup.find_all()
    '''
