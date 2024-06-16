import logging
import colorlog
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
import os
import re
import random

website_counts = {}

#Webdriver initialization
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
)

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

NICHE_NAME = "real_estate"

if not os.path.exists(NICHE_NAME):
    os.makedirs(NICHE_NAME)


def close_cookie_prompt(driver):
    """Close cookie prompt if found"""

    # Define the keywords to search for
    keywords = ["cookie", "reject", "dismiss", "no thanks", "refuse", "close", "ignore"]

    # Iterate over all elements in the HTML
    elements = driver.find_elements(By.XPATH, "//*")
    for element in elements:
        # Check tag name, class name and id for keywords
        tag_name = element.tag_name
        class_name = element.get_attribute("class") or ""
        id_name = element.get_attribute("id") or ""

        # Check for SVG shapes forming an 'X'
        svg_elements = element.find_elements(By.XPATH, ".//svg")
        for svg_element in svg_elements:
            svg_data = svg_element.get_attribute("outerHTML").lower()
            if "x" in svg_data:
                # We found an 'X' SVG shape, indicating a close button
                return svg_element

        for keyword in keywords:
            if keyword in tag_name or keyword in class_name or keyword in id_name:
                # We found a keyword, now check for buttons within the element
                button_elements = element.find_elements(By.XPATH, ".//button")
                for button in button_elements:
                    button_text = button.text.lower()
                    if any(word in button_text for word in ["close", "reject"]):
                        # Check if clicking this button leads to another page
                        button_link = button.get_attribute("href")
                        if not button_link or urljoin(driver.current_url, button_link) == driver.current_url:
                            # It's safe to click the button, as it doesn't navigate away
                            return button
    return None


def extract_text(soup):
    tags = ['title', 'meta', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'div', 'span', 'td', 'th']
    text_list = []

    for tag in tags:
        for element in soup.find_all(tag):
            text = element.get_text(strip=True)
            if text:  # skip empty strings
                text_list.append(text)

    return text_list

def save_text(url, text_list):
    global website_counts
    parsed_url = urlparse(url)
    website_name = parsed_url.netloc.replace("www.", "")
    count =  website_counts.get(website_name, 0) + 1
    website_counts[website_name] = count

    filename = os.path.join(NICHE_NAME, f"{website_name}_{count}.txt")

    try:
        with open(filename, "w") as file:
            for text in text_list:
                file.write(text + "\n")
    except (IOError, OSError) as e:
        logger.critical(f"Critical error occurred while trying to write to {filename}: {e}")
        raise


def same_domain(url1, url2):
    return urlparse(url1).netloc == urlparse(url2).netloc



def getLinks():
    return [("https://hubermanlab.com", 0), ("https://listings.com", 0), ("https://www.google.com", 0)]

def opacity_state_changed(old_state, new_state):
    for key in old_state.keys():
        if old_state[key] != new_state[key]:
            return True
    return False

def detect_js_libraries(driver):
    libraries = {
        'React': '!!window.React',
        'Angular': '!!window.angular',
        'jQuery': '!!window.jQuery',
    }
    library_detection = {}
    for lib, command in libraries.items():
        try:
            library_detection[lib] = driver.execute_script(f'return {command};')
        except WebDriverException:
            library_detection[lib] = False
    return library_detection


def handle_popup(element):

    try:
        # Try to close the popup with escape key
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        logger.info("Attempted to close popup with escape key.")
    except Exception as e:
        logger.error(f"Error when trying to close the popup with escape key: {e}")

    try:
        # Get the current URL
        current_url = driver.current_url

        # Check if the element contains a button or link that might be used to close a popup
        close_elements = element.find_elements(By.XPATH,".//*[self::a or self::button]")
        if not close_elements:
            logger.info("No buttons or links found in the new element.")
            return False

        # Try to click all buttons or links found
        for close_el in close_elements:
            try:
                # Check if the button or link text contains "close", "dismiss", or "cancel"
                button_text = close_el.text.lower()
                if 'close' in button_text or 'dismiss' in button_text or 'cancel' in button_text:
                    close_el.click()
                    logger.info("Clicked a close/dismiss/cancel button in the new element.")
                    return True
                # If the text does not contain "close", "dismiss", or "cancel", check if it might be an "X" button
                elif close_el.get_attribute('class').lower().contains('close') or close_el.get_attribute('id').lower().contains('close'):
                    close_el.click()
                    logger.info("Clicked a close button (detected via class or id) in the new element.")
                    return True
                # If it's a link, check if it leads to a different page
                elif close_el.tag_name.lower() == 'a':
                    link_url = close_el.get_attribute('href')
                    if link_url and link_url != current_url:
                        logger.info("Skipped clicking a link that leads to a different page.")
                        continue
            except Exception as e:
                logger.error(f"Could not click the button or link: {e}")

        return False

    except Exception as e:
        logger.error(f"Error when trying to handle the popup: {e}")
        return False


def get_opacities(driver):
    elements_to_check = ['body', 'div', 'main', 'section', 'article', 'aside', 'nav', 'header', 'footer', '.container', '.container-fluid', '.row']
    opacities = {}

    for element in elements_to_check:
        try:
            if element.startswith('.'):  # It's a class
                web_elements = driver.find_elements(By.CLASS_NAME, element[1:])  # Remove the dot
            else:  # It's a tag
                web_elements = driver.find_elements(By.TAG_NAME,element)

            for web_element in web_elements:
                if web_element.is_displayed():  # Check if the element is visible
                    opacity = driver.execute_script("return window.getComputedStyle(arguments[0]).opacity;", web_element)
                    opacities[element] = opacity
                    break  # Stop after finding the first visible element
            else:
                opacities[element] = None  # No visible elements found

        except NoSuchElementException:
            opacities[element] = None  # Element not found on the page

    return opacities

def is_scrollable(driver):
    script = '''
        return document.body.scrollHeight > window.innerHeight;
    '''
    return driver.execute_script(script)


def move_mouse_randomly(driver, element, num_movements):
    actions = ActionChains(driver)
    
    for _ in range(num_movements):
        x_offset = random.randint(0, 100)
        y_offset = random.randint(0, 100)
        actions.move_to_element_with_offset(element, x_offset, y_offset).perform()

def scrapeFirstPage():
    global website_counts
    urls_to_visit =  getLinks()
    visited_urls = set()
    page_text = {}
    current_website = None
    
    while urls_to_visit:
        url, depth = urls_to_visit.pop(0)
        website_name = urlparse(url).hostname.replace("www.", "").split('.')[0]

        print(url, depth)

        if website_name != current_website:
            
            current_website = website_name

        logger.info(f"Visiting URL {url} at depth {depth}")
        if url in visited_urls or depth > 2:
            continue

        try:
            driver.get(url)
        except TimeoutException:
            logger.warning(f"Timeout accessing {url}")
            continue
        except WebDriverException as e:
            logger.error(f"Error accessing {url}: {e}")
            continue

        while driver.execute_script("return document.readyState;") != "complete":
            time.sleep(random.uniform(0.1, 1))
        
        time.sleep(random.randint(2, 7))

        close_button = close_cookie_prompt(driver)
        if close_button:
            close_button.click()

        # Perform the second check for popups/modals
        last_opacity_state = get_opacities(driver)
        last_scrollable_state = is_scrollable(driver)
        last_dom_state = driver.find_elements(By.XPATH, "//*")
        last_active_element = driver.switch_to.active_element

       
        active_element = driver.switch_to.active_element
        current_opacity_state = get_opacities(driver)
        current_scrollable_state = is_scrollable(driver)
        current_dom_state = driver.find_elements(By.XPATH, "//*")

        if opacity_state_changed(last_opacity_state, current_opacity_state) or current_scrollable_state != last_scrollable_state:  # Check for changes in opacity or scrollability
            logger.info("Opacity or scrollability has changed. Possibly due to a modal or popup.")
            last_opacity_state = current_opacity_state
            last_scrollable_state = current_scrollable_state
            last_active_element = active_element

                # Compare current DOM state with the last one to find new elements
            new_elements = [el for el in current_dom_state if el not in last_dom_state]
            for el in new_elements:
                handle_popup(el)
        
        move_mouse_randomly(driver, driver.find_element(By.TAG_NAME,'body'), 10)
        #To be removed later and subsitute with the model data to simulate real user behavior
        driver.execute_script("window.scrollBy(0, 200);")


        # Perform the second check for popups/modals
        last_opacity_state = get_opacities(driver)
        last_scrollable_state = is_scrollable(driver)
        last_dom_state = driver.find_elements(By.XPATH, "//*")
        last_active_element = driver.switch_to.active_element

        # Popup/modal detection code
        current_opacity_state = get_opacities(driver)
        current_scrollable_state = is_scrollable(driver)
        current_dom_state = driver.find_elements(By.XPATH,"//*")
        active_element = driver.switch_to.active_element

        if opacity_state_changed(last_opacity_state, current_opacity_state) or current_scrollable_state != last_scrollable_state or active_element != last_active_element:
            logger.info("Opacity or scrollability has changed or a new element has received focus. Possibly due to a modal or popup.")
            last_opacity_state = current_opacity_state
            last_scrollable_state = current_scrollable_state
            last_active_element = active_element

            new_elements = [el for el in current_dom_state if el not in last_dom_state]
            for el in new_elements:
                handle_popup(el)
        
        # Detect JS libraries after loading the page
        js_libraries = detect_js_libraries(driver)
        logger.info(f"Detected JS libraries: {js_libraries}")

        # Heuristic: wait for dynamic content to load based on detected libraries
        if js_libraries['React'] or js_libraries['Angular'] or js_libraries['jQuery']:
            logger.info("Waiting for dynamic content to load")
            time.sleep(5)  # adjust this delay as needed

        visited_urls.add(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text_list = extract_text(soup)
        page_text[url] = text_list

        save_text(url, text_list)

        for a in soup.find_all('a'):
            href = a.get('href')
            full_url = urljoin(url, href)
            if same_domain(url, full_url) and full_url not in visited_urls and full_url not in urls_to_visit:
                urls_to_visit.append((full_url, depth + 1))
        print(urls_to_visit)
    driver.quit()
    
scrapeFirstPage()
