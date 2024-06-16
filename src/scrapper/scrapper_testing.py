from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from urllib.parse import urljoin, urlparse
from selenium.webdriver.support.ui import WebDriverWait
import time 

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

class ElementChecker:
    def __init__(self, driver, xpath):
        self.driver = driver
        self.xpath = xpath
        self.element = driver.find_element(By.XPATH, xpath)

    def is_element_present(self):
        try:
            self.driver.find_element(By.XPATH, self.xpath)
            return True
        except NoSuchElementException:
            return False

    def is_display_none(self):
        display_property = self.driver.execute_script("return window.getComputedStyle(arguments[0]).display;", self.element)
        return display_property == "none"

    def is_visibility_hidden(self):
        visibility_property = self.driver.execute_script("return window.getComputedStyle(arguments[0]).visibility;", self.element)
        return visibility_property == "hidden"

    def is_off_screen(self):
        position_property = self.driver.execute_script("return arguments[0].getBoundingClientRect();", self.element)
        return position_property['x'] < 0 or position_property['y'] < 0

    def is_opacity_zero(self):
        opacity_property = self.driver.execute_script("return window.getComputedStyle(arguments[0]).opacity;", self.element)
        return opacity_property == "0"


class AnyCheckTrue:
    def __init__(self, element_checker):
        self.element_checker = element_checker

    def __call__(self, driver):
        return any([
            self.element_checker.is_element_present(),
            self.element_checker.is_display_none(),
            self.element_checker.is_visibility_hidden(),
            self.element_checker.is_off_screen(),
            self.element_checker.is_opacity_zero()
        ])



def get_xpath(element):
    components = []
    child = element if element.name != '[document]' else element.children[0]
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if siblings == [child] else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)





    

def handle_popups():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    buttons =  soup.find_all('button')
    # Initialize an empty dictionary to hold the attributes
    attributes = {}

    # List of attribute names
    attr_names = ['id', 'class', 'title', 'aria-label']

    # List of keywords to search for
    keywords  = ["reject", "dismiss", "no thanks", "refuse", "close", "ignore", "cancel", "leave", "exit", "later", "decline", "not now", "hide", "deny", "remove","turn off", "not interested"]
    buttons_xpath = []
    for button in buttons:
        for name in attr_names:
            # Only store the attribute if it's not None
            attr_value = button.get(name)
            if attr_value is not None:
                attributes[name] = attr_value

                # If attribute value is a list, loop over its elements
                if isinstance(attr_value, list):
                    for value in attr_value:
                        # Check if the attribute value contains any of the keywords
                        for keyword in keywords:
                            if keyword.lower() in value.lower():
                                print(f"The word '{keyword}' was found in the attribute: {name}, value: {value}")
                                buttons_xpath.append(get_xpath(button))
                else:
                    # If attribute value is not a list, just check it directly
                    for keyword in keywords:
                        if keyword.lower() in attr_value.lower():
                            print(f"The word '{keyword}' was found in the attribute: {name}, value: {attr_value}")
                            buttons_xpath.append(get_xpath(button))

    return buttons_xpath

def click():
    buttons_xpath = handle_popups()  # I'm assuming this function returns a list of XPaths
    for button in buttons_xpath:
        try:
            button_element = driver.find_element(By.XPATH, button)
            button_element.click()
            print(f"Clicked on {button}")

            element_checker = ElementChecker(driver, button)

            # Wait until at least one check passes
            WebDriverWait(driver, 10).until(AnyCheckTrue(element_checker))

        except TimeoutException:
            print(f"Timeout error on {driver.current_url}. None of the checks passed for button: {button}")
        except Exception as e:
            print(f"Error on {driver.current_url} for button: {button}. Error message: {str(e)}")



driver.get("https://www.techradar.com/news/best-phone")
click()

