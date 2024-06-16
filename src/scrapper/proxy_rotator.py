import redis
import asyncio
import random
import os
import time
import requests
import argparse
from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock
import asyncio
import httpx
from fastapi import HTTPException
import logging
from starlette.requests import Request
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Response
import io  # For BytesIO
from typing import Dict, List
import os
from couchbase.cluster import Cluster
from couchbase.exceptions import DocumentNotFoundException
from couchbase_utilities.couchbase_connection_manager import CouchbaseConnectionManager
from dotenv import load_dotenv
import json


class ScoreBasedProxyRotator:
    def __init__(self, success_factor=1.1, failure_factor=0.9, threshold=0.1, timeout=5.0):
        load_dotenv()
        self.document_id = os.getenv("DOCUMENT_ID")
        self.success_factor = success_factor
        self.failure_factor = failure_factor
        self.threshold = threshold
        self.timeout = timeout
        #yaml
        self.zk_client = KazooClient(hosts='127.0.0.1:2181')
        self.redis = redis.Redis(host='localhost', port=44432, db=0)
        #Redis database to keep count of the number of instances connected to a proxy
        self.redis_persistence = redis.Redis(host='localhost', port=4432, db=1)
        self.scores = None
        self.total_score = 0
        self.proxies = []
        #try:
        #    self.load_scores()
        #except Exception as e:
        #    print(f'The scores are not in yet: {e}')

        
    # ...
    """
    def init_redis(self):       
        # Fetch new proxies and populate the Redis database
        # Remember that doing this like this without assigning to variables is safer
        self.fetch_new_proxies()
        print(self.proxies)
        for proxy in self.proxies:
            # We're using a helper method `add_proxy` that we've already defined.
            self.add_proxy(proxy, 1.0)
    """

    async def patch_article(self, proxy_list):
  
        try:
            cluster = CouchbaseConnectionManager().get_connection()
            cluster_bucket = cluster.bucket(os.getenv("BUCKET_NAME"))
            cluster_collection = cluster_bucket.default_collection()
            result = cluster_collection.upsert(self.document_id,proxy_list)
            print(result)
        except DocumentNotFoundException:
            raise HTTPException(
                status_code=404,
                detail="Resource does not exist",
            )
        except Exception as e:
            return {"success": False, "error": str(e)}



    async def fetch_new_proxies(self):
        
        async with httpx.AsyncClient() as client:
                
            url = "https://api.proxyscrape.com/v2/"
            params = {
                "request": "displayproxies",
                "protocol": "socks4",
                "timeout": "10000",
                "country": "all",
                "ssl": "all",
                "anonymity": "all"
            }
            response = await client.get(url, params=params)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to upload image: {response.text}"
                )
             # Accessing and printing various attributes of the response object
            
            proxies = response.text
            proxy_list = proxies.split('\n')
            proxy_list = [element.strip('\r') for element in proxy_list if element]
            proxy_list_dict = {"proxies": proxy_list}
            json_proxy_list = json.dumps(proxy_list_dict)
            print (json_proxy_list)
            await self.patch_article(json_proxy_list)

    def add_proxy(self, proxy_details, score):
        # Assuming proxy_details is a dictionary with keys 'ip', 'port', 'username', and 'password'
        key = f"{proxy_details['ip']}:{proxy_details['port']}:{proxy_details['username']}:{proxy_details['password']}"
        self.redis.set(key, score)


    def load_scores(self):
        self.scores = {}
        keys = self.redis.keys('*')
        self.get_scores = self.redis.mget(keys)

        for key, score in zip(keys, self.get_scores):
            key_str = key.decode('utf-8')  # convert bytes to string
            score_str = float (score.decode('utf-8'))
            self.total_score = self.total_score + score_str
            self.scores[key_str] = score_str


#If proxies esaurated returns none. Remember to handle it when you call it
#Remember to implement the decrement elsewhere in the code when you call driver.quit
    def get_proxy(self):
        lock = Lock(self.zk_client, '/proxy_lock')
        with lock:
            available_proxies = []
            for proxy_str, _ in self.scores.items():
                usage_count_key = f"usage:{proxy_str}"
                usage_count = int(self.redis_persistence.get(usage_count_key) or 0)
                
                if usage_count < 3:
                    available_proxies.append(proxy_str)
            
            if not available_proxies:
                print("All proxies have reached maximum usage count.")
                return None  # or raise a custom exception

            probabilities = [self.scores[proxy] / self.total_score for proxy in available_proxies]
            proxy_str = random.choices(available_proxies, weights=probabilities, k=1)[0]
            proxy_info = dict(zip(['ip', 'port', 'username', 'password'], proxy_str.split(':')))
            
            # Increment the usage count in Redis
            usage_count_key = f"usage:{proxy_str}"
            self.redis_persistence.set(usage_count_key, int(self.redis_persistence.get(usage_count_key) or 0) + 1)
            
            return proxy_info   
        

    def send_request(self, url, proxy, max_retries=3):
        for _ in range(max_retries):
            try:
                proxy_auth = (proxy['username'], proxy['password'])
                proxy_url = f'http://{proxy["ip"]}:{proxy["port"]}'
                response = requests.get(url, proxies={"http": proxy_url, "https": proxy_url}, auth=proxy_auth, timeout=self.timeout)
                if response.status == 200:
                    self.update_score(proxy, True)
                    return proxy
                else:
                    self.update_score(proxy, False)
                            
            except Exception as e:
                self.update_score(proxy, False)
        raise Exception(f"Failed to send request after {max_retries} attempts")
    


    def update_score(self, proxy, success):
        key = f"{proxy['ip']}:{proxy['port']}:{proxy['username']}:{proxy['password']}"

        if success:
            self.total_score -= self.scores[key]
            self.scores[key] *= self.success_factor
            self.total_score += self.scores[key]
        else:
            self.total_score -= self.scores[key]
            self.scores[key] *= self.failure_factor
            self.total_score += self.scores[key]

        if self.scores[key] < self.threshold:
            self.total_score -= self.scores[key]
            del self.scores[key]

        else:
            self.redis.set(key, self.scores[key])


    def reset_database(self):
        self.redis.flushdb()
        self.init_redis()   

#Watch_file block execution run it on its own thread
    def watch_file(self, filepath):
        last_modified_time = os.path.getmtime(filepath)
        while True:
            time.sleep(1)  # check every second
            current_modified_time = os.path.getmtime(filepath)
            if current_modified_time != last_modified_time:
                last_modified_time = current_modified_time
                self.file_change_event.set()  # file has changed, so set the Event


    def run(self):
        parser = argparse.ArgumentParser()

        # Define the command-line arguments
        parser.add_argument("--reset_database", action="store_true", help="Reset the database")
        parser.add_argument("--init_redis", action="store_true", help="Initialize Redis")

        # Parse the command-line arguments
        args = parser.parse_args()

        # Based on the command-line arguments, call the appropriate methods
        if args.reset_database:
            self.reset_database()

        if args.init_redis:
            self.init_redis()


if __name__ == "__main__":
    # Instantiate your class
    async def main():
        proxy_rotator = ScoreBasedProxyRotator()
        await proxy_rotator.fetch_new_proxies()
    asyncio.run(main())
    # Run the command-line interface
    #proxy_rotator.run()

#Remember to add the following code to handle when proxies are loaded each month
'''
# define a main function
async def main():
    # start both coroutines
    await asyncio.gather(my_class.watch_file('myfile.txt'), my_class.do_something_on_file_change())

# run the main function
asyncio.run(main())

'''

'''
async def main():
    redis_start = await MyClass.create()
    chosen_proxy = redis_start.get_proxy()
    await redis_start.send_request('https://fandomwire.com/', chosen_proxy)
    
    '''







'''
import asyncio
import aiomysql
from aiomultiprocess import Pool
import random
import aiohttp
from aiohttp import ClientSession, ClientTimeout


class ScoreBasedProxyRotator:
    

    def __init__(self, success_factor=1.1, failure_factor=0.9, threshold=0.1, timeout=5.0):
        self.success_factor = success_factor
        self.failure_factor = failure_factor
        self.threshold = threshold
        self.timeout = timeout

        # Database connection parameters
        self.db_params = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'Iphonesucks@94',
            'db': 'proxy_scores',
            'autocommit': True
        }

    @classmethod
    async def create(cls, success_factor=1.1, failure_factor=0.9, threshold=0.1, timeout=5.0):
        self = cls(success_factor, failure_factor, threshold, timeout)
        await self.init_db()
        self.proxies = await self.load_proxies()
        self.scores = await self.load_scores()
        self.total_score = sum(self.scores.values())

        # If there are no proxies loaded from the database, initialize them from a file
        if not self.proxies:
            self.initialize_proxies('proxies.txt')
            self.scores = {proxy: 1 for proxy in self.proxies}
            self.total_score = len(self.proxies)
            
        return self

    async def cleanup(self):
        await self.close_pool()
    
    def initialize_proxies(self, filepath):
        with open(filepath, 'r') as f:
            self.proxies = [line.strip() for line in f]


    async def init_db(self):
        try:
            self.pool = await aiomysql.create_pool(**self.db_params)
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        CREATE TABLE IF NOT EXISTS scores (
                            ip VARCHAR(255),
                            port INT,
                            username VARCHAR(255),
                            password VARCHAR(255),
                            score DOUBLE,
                            PRIMARY KEY(ip, port)
                        )
                    """)

                    # Fetch new proxies and populate the database
                    proxies = await self.fetch_new_proxies()
                    for proxy in proxies:
                        try:
                            await cur.execute("""
                                INSERT INTO scores (ip, port, username, password, score)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (proxy['ip'], proxy['port'], proxy['username'], proxy['password'], 1.0))  # Assuming a default score of 1.0 for new proxies
                        except aiomysql.IntegrityError:
                            print(f"Proxy {proxy['ip']}:{proxy['port']} already exists in the table.")
        except aiomysql.MySQLError as e:
            print(f"A MySQL error occurred: {e}")



    async def close_pool(self):
        self.pool.close()
        await self.pool.wait_closed()

#To be changed 
    
    async def load_scores(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM scores")
                rows = await cur.fetchall()
                self.scores = {proxy: row[4] for proxy, row in zip(self.proxies, rows)}


        return self.scores
    

    async def load_proxies(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT ip, port, username, password FROM scores")
                rows = await cur.fetchall()
                self.proxies = [f"{row[0]}:{row[1]}:{row[2]}:{row[3]}" for row in rows]






    async def save_scores(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                for proxy, score in self.scores.items():
                    await cur.execute("""
                        REPLACE INTO scores 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (proxy['ip'], proxy['port'], proxy['username'], proxy['password'], score))

        await self.close_pool()



    async def update_score(self, proxy, success):
        key = f"{proxy['ip']}:{proxy['port']}:{proxy['username']}:{proxy['password']}"

        if success:
            self.total_score -= self.scores[key]
            self.scores[key] *= self.success_factor
            self.total_score += self.scores[key]
        else:
            self.total_score -= self.scores[key]
            self.scores[key] *= self.failure_factor
            self.total_score += self.scores[key]

        if self.scores[key] < self.threshold:
            self.total_score -= self.scores[key]
            del self.scores[key]

        # Persist scores to database
        await self.save_scores()




    async def send_request(self, url, proxy, max_retries=3):
        for _ in range(max_retries):
            try:
                timeout = ClientTimeout(total=self.timeout)
                async with ClientSession(timeout=timeout) as session:
                    proxy_auth = aiohttp.BasicAuth(proxy['username'], proxy['password'])
                    proxy_url = f'http://{proxy["ip"]}:{proxy["port"]}'
                    async with session.get(url, proxy=proxy_url, proxy_auth=proxy_auth) as response:
                        if response.status == 200:
                            await self.update_score(proxy, True)
                            return await response.text()
                        else:
                            await self.update_score(proxy, False)
            except Exception as e:
                await self.update_score(proxy, False)
        raise Exception(f"Failed to send request after {max_retries} attempts")


    #To be deleted probably
    async def validate_proxy(self, proxy):
        try:
            await self.send_request('http://whatismyip.com', max_retries=1)
            return True
        except:
            return False
    #To be deleted probably
    async def validate_proxies(self):
        async with Pool() as pool:
            results = await pool.map(self.validate_proxy, self.proxies)
        self.proxies = [proxy for proxy, valid in zip(self.proxies, results) if valid]


    def get_proxy(self):
        probabilities = [score / self.total_score for score in self.scores.values()]
        proxy_str = random.choices(list(self.scores.keys()), weights=probabilities, k=1)[0]
        proxy_info = dict(zip(['ip', 'port', 'username', 'password'], proxy_str.split(':')))
        return proxy_info


    

    async def fetch_new_proxies(self):
        try:
            with open('proxies.txt', 'r') as f:
                proxies = []
                for line in f:
                    try:
                        ip, port, username, password = line.strip().split(':')
                        try:
                            port = int(port)  # This could raise a ValueError if port is not a number
                        except ValueError:
                            print(f"Non-numeric port value in proxies.txt: {port}")
                            continue  # Skip the current line and proceed to the next


                        proxies.append({
                            'ip': ip,
                            'port': port,
                            'username': username,
                            'password': password,
                            'score' : 1
                        })
                    except ValueError:
                        print(f"Malformed line in proxies.txt: {line.strip()}")

                for proxy in proxies:
                    #change the ip to some ip or server of mine, probably to the address you wanna crawl
                    self.send_request('http://whatismyip.com', proxy)
            
             #Delete this return later  
            return proxies
        except FileNotFoundError:
            print("The file proxies.txt was not found.")
            return []

    
#Start here with redis drop and reload the new proxies. 
    async def reset_database(self):
        self.pool = await aiomysql.create_pool(host=self.db_params['host'], port=self.db_params['port'],user=self.db_params['user'], password=self.db_params['password'], autocommit=True)
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Drop the database if it exists
                await cur.execute(f"DROP DATABASE IF EXISTS {self.db_params['db']}")
                # Create the database
                await cur.execute(f"CREATE DATABASE {self.db_params['db']}")

        self.pool = await aiomysql.create_pool(**self.db_params)
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Create the table in the newly created database
                await cur.execute("CREATE TABLE IF NOT EXISTS scores (proxy VARCHAR(255) PRIMARY KEY, score DOUBLE)")


        await self.close_pool()

'''
    

