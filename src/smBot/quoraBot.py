from contextlib import nullcontext
from genericpath import exists
from http import cookies
from browserSetup import mozilla
import os
from bs4 import BeautifulSoup
import random 
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pickle
import pathlib

#Implement user input such as cookies
#def handleUserInput():

def getPath():
    currentPath = os.path.dirname(__file__)
    finalPath = currentPath + '/cookies/cookies.pkl'
    result = os.path.isfile(finalPath)
    return result

def randomizeWidth():
    resList = [(1920,1080), (1366,768), (1440,900), (1536,864), (2560,1440), (1680,1050), (1280,720), (1280,800), (1792,1120), (1600,900)]
    randomize = random.randint(0, len(resList)-1)
    pickResolution = resList[randomize]
    width = pickResolution[0]
    return width 

def manageQuora():
    
    resList = {1920:1080, 1366:768, 1440:900, 1536:864, 2560:1440, 1680:1050, 1280:720, 1280:800, 1792:1120, 1600:900}
    windowSize = randomizeWidth()
    print(windowSize)
    print(resList[windowSize])
    instance = mozilla(windowSize, resList[windowSize])
    if isinstance(instance, mozilla) == True:
        driver = instance.driver
        url = "http://www.quora.com"
        driver.get(url)
        time.sleep(3)
        email = "skenderixhulio@gmail.com"
        uname = driver.find_element("id", "email")
        time.sleep(1)
        uname.send_keys(email)
        password = "Europiani@2013"
        getPassword = driver.find_element("id", "password")
        time.sleep(1)
        getPassword.send_keys(password)
        time.sleep(10)
        try:
            check_boxes =  driver.find_element("id", "rc-anchor-container")
            check_boxes.click()
        except Exception as error:
            pass
        try:
            loginButton = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[4]/button")
            loginButton.click()
        except Exception as e:
            print('Login not found')
        time.sleep(5)
        
    if getPath() == True:
        print ("exists")
    else:
        print("doesn't")
        
        cookies = driver.get_cookies()
        #if os.path.isfile('./cookies/cookies.pkl'):
        pickle.dump(cookies, open("./cookies/cookies.pkl", "wb"))

def likePost():
    link = ""
    #like posts
    return null


def answerQuestions():
    #answer questions
    return null



manageQuora()
