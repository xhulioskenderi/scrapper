import os
import time

def watch_file(filepath):
    last_modified_time = os.path.getmtime(filepath)
    while True:
        time.sleep(1)  # check every second
        current_modified_time = os.path.getmtime(filepath)
        if current_modified_time != last_modified_time:
            print(f"File {filepath} has been modified")
            last_modified_time = current_modified_time


# use it
watch_file('/Users/xhulioskenderi/Desktop/CryptoP/openai-quickstart-python/scrapper/proxies.txt')
