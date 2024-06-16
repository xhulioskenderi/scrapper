import requests
import socks  # PySocks
import socket
import sys
import os
#fix the import figure out how to make them a package or something
sys.path.append(os.path.abspath(os.path.join('..')))

from browser_setup_code import Chrome  # replace 'YourClass' with your class name
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import uuid
from start_and_route import StartInfrastructure


#This might need some changes
webdriver_instance = StartInfrastructure('https://www.paginegialle.it')
webdriver = webdriver_instance.setup()
webdriver.get("https://www.paginegialle.it")
# Use WebDriverWait to ensure the page is fully loaded
wait = WebDriverWait(webdriver.driver, 10)

# Here, replace 'div-classname' with your actual class name
div_class_path = "div.categorie-macro__box-corr__el categorie-macro__box-corr__el--4-mob"

# Wait until the div with the given class name is loaded
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, div_class_path)))

# Find the li tags inside the div
lis_in_div = webdriver.driver.find_elements_by_css_selector(f"{div_class_path} ul li")

# Iterate over the li tags and print out the href attributes
for li in lis_in_div:
    a = li.find_element_by_tag_name("a")
    print(a.get_attribute("href"))

# Close the browser
webdriver.quit()



'''
def send_request(url, proxy, max_retries=3):
        for _ in range(max_retries):
            try:
                proxy_parts = proxy.split(':')
                proxy_dict = {
                'ip': proxy_parts[0],
                'port': int (proxy_parts[1]),
                'username': proxy_parts[2],
                'password': proxy_parts[3],
            }
                
                socks.set_default_proxy(socks.SOCKS5, proxy_dict['ip'], proxy_dict['port'], username=proxy_dict['username'], password=proxy_dict['password'])
                socket.socket = socks.socksocket
                response = requests.get(url)
               

                if response.status_code == 200:
                    print("Works")
                    return proxy
                else:
                    print(f"Doesn't work. HTTP status code: {response.status_code}")
                            
            except Exception as e:
                print(f'There was an exception {e}')
        raise Exception(f"Failed to send request after {max_retries} attempts")

send_request('http://example.com','45.94.47.66:8110:dbrpczyf:tm53d0vp7o4p')

'''

'''
def send_request(url, local_proxy_port, max_retries=3):
    for _ in range(max_retries):
        try:
            proxies = {
                'http': f'socks5://localhost:{local_proxy_port}',
                'https': f'socks5://localhost:{local_proxy_port}',
            }
            
            response = requests.get(url, proxies=proxies)

            if response.status_code == 200:
                print("Works")
            else:
                print(f"Doesn't work. HTTP status code: {response.status_code}")

        except Exception as e:
            print(f'There was an exception {e}')

    raise Exception(f"Failed to send request after {max_retries} attempts")

send_request('http://example.com', 8001)
'''