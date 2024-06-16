import hashlib
from bisect import bisect_left
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import redis
import random
import time
import logging
from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock


zk = KazooClient(hosts='127.0.0.1:2181')  # Point to your Zookeeper server
zk.start()
reserved_pool_lock_key = "/lock/reserved_pool"
global_lock = Lock(zk, "/lock/reserved_pool")

def acquire_lock(lock, retries, delay):
    for i in range(1, retries + 1):
        acquired = lock.acquire(blocking=False)
        if acquired:
            return True, None
        else:
            jitter = random.uniform(-0.1, 0.1)
            time.sleep(delay + jitter)
    logging.error(f"Failed to acquire lock after {retries} retries")
    return False, f"Failed to acquire lock after {retries} retries"

def release_lock(lock):
    try:
        lock.release()
        return True
    except Exception as e:
        logging.error(f"Failed to release lock: {e}")
        return False


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        a = s.getsockname()[1]
        s.close()
        return a

class ConsistentHashingLoadBalancer:
    def __init__(self, nodes=None, replicas=100):
        self.ring = {}
        self.sorted_key = []
        self.replicas = replicas
        if nodes:
            for node in nodes:
                self.add_node(node)
        self.connection_pool = {}
        for node in nodes or []:
            self.connection_pool[node] = Queue()
            for _ in range(5):  # Initialize 5 connections per node
                conn = self.create_new_connection(node, find_free_port())
                self.connection_pool[node].put(conn)
    

    def create_new_connection(self, node, outgoing_port):

        target_host, target_port = node.replace("http://", "").split(":")

        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # Set Keepalive here
        

        if outgoing_port:
            new_socket.bind(("0.0.0.0", outgoing_port))

        new_socket.connect((target_host, int(target_port)))
        return new_socket


    
    def get_connection(self, node, outgoing_port):
       
        return self.create_new_connection(node, outgoing_port)

        
    def return_connection(self, node, conn):
        self.connection_pool[node].put(conn)

    #Hashes server nodes and the specific identifiers
    def hash_key(self, key):
        m = hashlib.md5()
        m.update(str(key).encode('utf-8'))
        return int(m.hexdigest(), 16)
    
    #Sorts the nodes for faster lookup via binary search (O(logn))
    def add_node(self, node):
        for i in range(self.replicas):
            hash_value = self.hash_key(f"{node}:{i}")
            self.ring[hash_value] = node
            self.sorted_key.append(hash_value)
        self.sorted_key.sort()

    #Reverse the process of adding nodes to remove them
    def remove_node(self, node):
        for i in range(self.replicas):
            hash_value = self.hash_key(f"{node}:{i}")
            del self.ring[hash_value]
            self.sorted_key.remove(hash_value)
    
    #Places the traffic based on the port number 
    def get_node(self, incoming_port):
        if self.ring:
            hash_value = self.hash_key(incoming_port)
            idx = bisect_left(self.sorted_key, hash_value)
            if idx == len(self.sorted_key):
                idx = 0
            return self.ring[self.sorted_key[idx]]

reserved_pool = {}






def handle_client(load_balancer, client_socket, client_address):
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    incoming_port = client_address[1]
    print(f"Handling incoming connection from port: {incoming_port}")  # Just for logging
    
    target_socket = None
    target_node = None

    target_node = load_balancer.get_node(incoming_port)
    print(f'Selected {target_node}')
    try:
        target_socket = load_balancer.get_connection(target_node, find_free_port())
        print(f'Selected{target_node}')
    except Exception as e:
        print(f"Error while creating connection: {e}")
        return

    try:
        while True:
            print("Waiting to receive data from client...")
            client_data = client_socket.recv(4096)
            print(f"Received data from client: {client_data}")
            
            if not client_data:
                print(f"Client at port {incoming_port} disconnected")
                break

            print("Sending data to target...")
            target_socket.send(client_data)
            
            print("Waiting to receive data from target...")
            target_data = target_socket.recv(4096)
            print(f"Received data from target: {target_data}")

            if not target_data:
                print("Backend server disconnected")
                break

            print("Sending data back to client...")
            client_socket.send(target_data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing target socket")
        target_socket.close()






if __name__ == "__main__":
    #print("Connecting to redis")

    #redis_client = redis.Redis(host='localhost', port=44432, db=2, decode_responses=True)

    print("starting_server")
    load_balancer = ConsistentHashingLoadBalancer(nodes=["http://localhost:8111", "http://localhost:8112", "http://localhost:8113"])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 9001))  # where it will listen
    server_socket.listen(5)  # Listen for up to 5 incoming connections in the queue

    with ThreadPoolExecutor(max_workers=20) as executor:
        while True:
            # Accept incoming connection
            client_sock, client_address = server_socket.accept()
            
            print(f"Accepted connection from {client_address}")
            
            executor.submit(handle_client, load_balancer, client_sock, client_address)