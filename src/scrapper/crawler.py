import time
import random
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from queue import Queue

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

class Crawler:
    def __init__(self, base_url, max_depth):
        self.base_url = base_url
        self.max_depth = max_depth
        self.domain_name = urlparse(base_url).netloc
        self.urls_queue = Queue()
        self.urls_queue.put((self.base_url, 0))
        self.discovered_urls = set()

    def start(self):
        while not self.urls_queue.empty():
            url, depth = self.urls_queue.get()

            if depth > self.max_depth:
                break

            try:
                self.crawl(url, depth)
            except requests.exceptions.RequestException as e:
                print(f"Failed to crawl {url}: {str(e)}")

            time.sleep(random.uniform(3, 10))  # Delay between requests

    def crawl(self, url, depth):
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue

            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

            if not is_valid(href):
                continue
            if href in self.discovered_urls:
                continue
            if self.domain_name not in href:
                continue
            if not parsed_href.path.endswith(('.html', '.htm', '.php', '.aspx', '')):
                continue
            
            with open('urls.txt', 'a') as f:
                f.write(f"{href}\n")


            print(f"Discovered URL: {href} at depth {depth}")
            self.discovered_urls.add(href)
            self.urls_queue.put((href, depth + 1))

crawler = Crawler("https://www.paginegialle.it", 10000)  # Set your URL and max_depth here
crawler.start()
