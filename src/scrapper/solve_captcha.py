from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from urllib.parse import urljoin, urlparse
from selenium.webdriver.support.ui import WebDriverWait
import time 
from selenium.webdriver.support import expected_conditions as EC
import threading
from twocaptcha import TwoCaptcha
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

lock = threading.Lock()
solver = TwoCaptcha('7e8dceb5fb46e4126280fea3ac56112d')
# navigate to your page



class CaptchaSolver:
    def __init__(self, api_key):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.lock = threading.Lock()
        self.solver = TwoCaptcha(api_key)

    def scan_for_buttons(self, captcha_element):
        try:
            print("Checking for buttons")
            parent_element = driver.execute_script("return arguments[0].parentNode;", captcha_element)
            print(parent_element)
            button_elements = driver.find_elements(By.TAG_NAME, 'button')
            print (button_elements)
            input_elements = driver.find_elements(By.XPATH, ".//input[@type='submit']")
            print(input_elements)
            captcha_y = captcha_element.location['y']
            min_distance = float('inf')
            window_size = driver.get_window_size()
            height = window_size['height']
            max_distance = height * 0.19  # Adjust the multiplier as needed
            submit_button = None
            word_check_list = ['submit', 'send', 'continue', 'proceed', 'verify', 'confirm', 'accept', 'apply', 'check']

            for button in button_elements + input_elements:
                try:
                    button_y = button.location['y']
                    if captcha_y < button_y < captcha_y + max_distance:
                        button_text = button.text.lower()
                        if any(word in button_text for word in word_check_list):
                            distance = button_y - captcha_y
                            if distance < min_distance:
                                min_distance = distance
                                submit_button = button
                except StaleElementReferenceException:
                    continue


            
            if submit_button is not None:
                # Scroll the submit_button into view
                driver.execute_script("arguments[0].scrollIntoView();", submit_button)
                # Wait until the submit_button is clickable and then click it
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(submit_button))
                submit_button.click()
                return True
            else:
                return False

        except (NoSuchElementException, TimeoutException):
            print("Either no button or input elements were found in the vicinity of the CAPTCHA or the CAPTCHA itself wasn't detected.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    script = '''
        // Create a global variable to store the captcha detection state
        window.captchaDetected = false;

        // Function to check for reCAPTCHA elements on page load
        function checkForCaptcha() {
            var iframes = document.getElementsByTagName('iframe');
            for (var i = 0; i < iframes.length; i++) {
                if (iframes[i].src.includes('google.com/recaptcha')) {
                    window.captchaDetected = true;
                    break;
                }
            }

            if (!window.captchaDetected) {
                var divs = document.getElementsByClassName('g-recaptcha');
                if (divs.length > 0) {
                    window.captchaDetected = true;
                }
            }
        }

        // Check for reCAPTCHA elements immediately
        checkForCaptcha();

        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    for (var i = 0; i < mutation.addedNodes.length; i++) {
                        var node = mutation.addedNodes[i];
                        if (node.nodeType === 1) { // Check if the node is an element node
                            if (node.tagName.toLowerCase() === 'iframe' && node.src.includes('google.com/recaptcha')) {
                                // Set the captcha detection state to true
                                window.captchaDetected = true;
                            }
                            if (node.className && node.className.includes('g-recaptcha')) {
                                // Set the captcha detection state to true
                                window.captchaDetected = true;
                            }
                        }
                    }
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });


            
        '''
    

    #Rememeber to handle feeding the target url 


    def check_for_captcha(self, target_url):
        while True:
            with lock:
                captcha_detected = driver.execute_script("return captchaDetected;")
                if captcha_detected:
                    
                    captcha_element = driver.find_element(By.CLASS_NAME,'g-recaptcha')
                    parent_element = driver.execute_script("return arguments[0].parentNode;", captcha_element)
                    button_elements = parent_element.find_elements(By.TAG_NAME, 'button')
                    input_elements = parent_element.find_elements(By.XPATH, ".//input[@type='submit']")
                    data_sitekey_value = captcha_element.get_attribute('data-sitekey')
                    time.sleep(2)
                    #Solver instance 
                    result = solver.recaptcha(data_sitekey_value,
                    url=target_url)
                    captcha_code = result.get('code')
                    time.sleep(2)
                    try:
                        script1 = "document.getElementById('g-recaptcha-response').value = '{}';".format(captcha_code)
                        driver.execute_script(script1)
                    except Exception as exception1:
                        print(f"An error occurred while executing the script: {exception1}")
                        return None

                    try:
                        driver.execute_script(script1)
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"An error occurred while setting the captcha response: {e}")

                    time.sleep(2)
                    driver.execute_script(script1)
                    time.sleep(2)

                    if self.scan_for_buttons(captcha_element):
                        return None
                    else:
                        ######################
                        ##    Change this   ##
                        ######################
                        pass
                    '''
                    try:
                        print("Checking for buttons")
                        parent_element = driver.execute_script("return arguments[0].parentNode;", captcha_element)
                        print(parent_element)
                        button_elements = driver.find_elements(By.TAG_NAME, 'button')
                        print (button_elements)
                        input_elements = driver.find_elements(By.XPATH, ".//input[@type='submit']")
                        print(input_elements)
                        captcha_y = captcha_element.location['y']
                        min_distance = float('inf')
                        window_size = driver.get_window_size()
                        height = window_size['height']
                        max_distance = height * 0.19  # Adjust the multiplier as needed
                        submit_button = None
                        word_check_list = ['submit', 'send', 'continue', 'proceed', 'verify', 'confirm', 'accept', 'apply', 'check']

                        for button in button_elements + input_elements:
                            try:
                                button_y = button.location['y']
                                if captcha_y < button_y < captcha_y + max_distance:
                                    button_text = button.text.lower()
                                    if any(word in button_text for word in word_check_list):
                                        distance = button_y - captcha_y
                                        if distance < min_distance:
                                            min_distance = distance
                                            submit_button = button
                            except StaleElementReferenceException:
                                continue

                        if submit_button is not None:
                            # Scroll the submit_button into view
                            driver.execute_script("arguments[0].scrollIntoView();", submit_button)
                            # Wait until the submit_button is clickable and then click it
                            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(submit_button))
                            submit_button.click()
                            return None

                    except (NoSuchElementException, TimeoutException):
                        print("Either no button or input elements were found in the vicinity of the CAPTCHA or the CAPTCHA itself wasn't detected.")
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")
                        '''



#Start the thread when calling this class like this 

#captcha_thread = threading.Thread(target=check_for_captcha)
#captcha_thread.start()





