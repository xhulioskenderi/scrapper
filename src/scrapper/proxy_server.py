import socketserver
import socket
import socks  # PySocks
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio
from proxy_rotator import ScoreBasedProxyRotator
from browser_setup_code import Chrome
import multiprocessing
import uuid
from selenium_instance_caching import CustomCache
import requests
import time
from threading import Thread

#Remember to implement this stuff with the proxy rotator . Note that there's still some work to be done().   


# Configure logging
logging.basicConfig(level=logging.DEBUG)

# ThreadPool for handling requests
executor = ThreadPoolExecutor(max_workers=10)

# Authorized clients
AUTHORIZED_CLIENTS = {
    '192.168.1.2',  # Replace with your authorized client IPs
    '192.168.1.3'
}

class Socks5ProxyHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        
    
    def heartbeat_mechanism(self, sock):
        try:
            while True:
                # Send heartbeat (PING message)
                sock.sendall(b'PING')
                
                # Wait for acknowledgment (PONG message)
                data = sock.recv(1024)
                
                if data == b'PONG':
                    logging.info(f"Heartbeat acknowledged for client: {self.client_address}")
                else:
                    logging.warning(f"Heartbeat failed for client: {self.client_address}, disconnecting.")
                    sock.close()
                    break
                
                # Wait before sending the next heartbeat
                time.sleep(5)
        
        except socket.timeout:
            logging.warning(f"Heartbeat timeout for client: {self.client_address}, disconnecting.")
            sock.close()
        
        except Exception as e:
            logging.error(f"Heartbeat exception: {type(e).__name__}, {e} for client: {self.client_address}")
            sock.close()
    
    def read_write(self, sock1, sock2):
        """
        logging.info(f"Starting read_write with {sock1} and {sock2}")

        buffer_size = 4096  # Fixed buffer size in bytes

        try:
            while True:
                logging.debug("Attempting to receive data")
                data = sock1.recv(buffer_size)
                if len(data) == 0:
                    break
                logging.debug(f"Data received: {data}")
                sock2.sendall(data)
                logging.debug("Data sent")
        except Exception as e:
            logging.error(f"Exception occurred in read_write: {type(e).__name__}, {e}")
        finally:
            logging.info("read_write completed")
        """
        
        logging.info(f"Starting read_write with {sock1} and {sock2}")
        # Adaptive Buffering Variables
        min_buffer_size = 1024  # minimum buffer size in bytes
        max_buffer_size = 8192  # maximum buffer size in bytes
        buffer_size = 4096  # initial buffer size in bytes
        total_received = 0  # total bytes received
        packet_count = 0  # total packets received
        avg_packet_size = 0  # average packet size

        try:
            while True:
                logging.debug("Attempting to receive data")  # Before recv
                data = sock1.recv(buffer_size)
                packet_size = len(data)
                logging.debug(f"Received data of size {packet_size} bytes: {data}")
                # Update average packet size
                total_received += packet_size
                packet_count += 1
                avg_packet_size = total_received / packet_count
                
                # Adapt buffer size
                if avg_packet_size > buffer_size * 1.5 and buffer_size < max_buffer_size:
                    buffer_size = min(max_buffer_size, buffer_size * 2)
                    logging.info(f"Increasing buffer size to {buffer_size}")
                
                elif avg_packet_size < buffer_size * 0.5 and buffer_size > min_buffer_size:
                    buffer_size = max(min_buffer_size, buffer_size // 2)
                    logging.info(f"Decreasing buffer size to {buffer_size}")
                if len(data) == 0:
                    break
                logging.debug(f"Data received: {data}")
                logging.debug("Attempting to send data")
                sock2.sendall(data)
                logging.debug(f"Data of size {packet_size} bytes sent successfully")
        except Exception as e:
            logging.error(f"Exception occurred in read_write: {type(e).__name__}, {e}")
            logging.error(f"Last received data before exception: {data}")
            logging.error(f"Last buffer size: {buffer_size}")
            logging.error(f"Last average packet size: {avg_packet_size}")
        finally:
            logging.info("read_write completed")
        
        


    def handle(self):
        logging.info(f"New connection established from: {self.client_address}")

        self.request.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.request.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        proxy = {'ip': '45.94.47.66', 'port': 8110, 'username': 'dbrpczyf', 'password': 'tm53d0vp7o4p'}
        ip = proxy['ip']
        remote_proxy_port = int (proxy['port'])
        username = proxy['username']
        password = proxy['password']
        sock = socks.socksocket()
        try:
            # Set timeouts
            sock.settimeout(20.0)

            # Set socket options for keep-alive and address reuse
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logging.info("Socket options set")

            # Connect to remote proxy
            sock.bind(('0.0.0.0', 0))
            sock.set_proxy(
                socks.SOCKS5,
                ip, 
                port=remote_proxy_port,
                username=username,
                password=password
                            
                    )
            logging.info(f"Proxy set with IP: {ip}, Port: {remote_proxy_port}")
            logging.info("Socket bound")
            # Utilize ThreadPool for handling requests
            executor.submit(self.read_write, self.request, sock)
            executor.submit(self.read_write, sock, self.request)
            #executor.submit(self.heartbeat_mechanism, self.request)


        except socket.timeout:
            logging.error("Socket operation timed out")
        except Exception as e: 
            sock.close()
            logging.error(f"Exception occurred in handle: {type(e).__name__}, {e}")
        finally:
            logging.info("Handle completed")



def start(local_proxy_port):
    with socketserver.ThreadingTCPServer(("localhost", local_proxy_port), Socks5ProxyHandler) as server:
        
        try:
            logging.info("Starting proxy server")
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        server.shutdown()
        logging.info("Shutting down proxy server")



if __name__ == '__main__':
    ports = [8111, 8112, 8113]  # Replace with your desired ports
    threads = []

    for port in ports:
        thread = Thread(target=start, args=(port,))
        thread.start()
        threads.append(thread)
        logging.info(f"Thread started for port {port}")

    for thread in threads:
        thread.join()