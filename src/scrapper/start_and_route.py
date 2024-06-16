import socket
from mini_proxy import MiniProxy
from proxy_rotator import ScoreBasedProxyRotator
from browser_setup_code import Chrome
import redis
import threading
import json
import logging

class StartInfrastructure:
    def __init__(self, website_name):
        self.website_name = website_name
        self.port_ip_association = redis.Redis(host='localhost', port=4432, db=2)
        self.incoming_outgoing_port = redis.Redis(host='localhost', port=4432, db=3)

    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            a = s.getsockname()[1]
            s.close()
            return a
#Takes the connection from the webdriver and connect to the load balancer 
    def direct_connect_to_load_balancer(self, client_socket, outgoing_port, target_host, target_port):

        try:
            target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target.bind(("0.0.0.0", outgoing_port))
            target.connect((target_host, target_port))

        except Exception as e:
            logging.error(f"Error connecting to load balancer: {e}")
            return
        
        while True:
            client_data = client_socket.recv(4096)
            if not client_data:
                break

            target.send(client_data)
            target_data = target.recv(4096)

            if not target_data:
                break

            client_socket.send(target_data)

        client_socket.close()
        target.close()

#Connects the webdriver to the server to then forward it to the load balancer 
    def server_loop(self, port1, outgoing_port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", port1))
        server.listen(5)

        while True:
            client_socket, addr = server.accept()
            #change this to the actual load balancer host
            target_host = 'load_balancer_host'
            target_port = 8000  # Load Balancer port

            direct_connect_thread = threading.Thread(
                target=self.direct_connect_to_load_balancer,
                args=(client_socket, outgoing_port, target_host, target_port)
            )
            direct_connect_thread.start()

        
    def setup(self):
        try:
            port1 = self.find_free_port()
            #port2 = self.find_free_port()
            outgoing_port = self.find_free_port()
            self.incoming_outgoing_port.set(port1,outgoing_port)
            proxy_tool = ScoreBasedProxyRotator()
            choose_proxy = proxy_tool.get_proxy()
            # Serialize the proxy info to a JSON string
            serialized_proxy_info = json.dumps(choose_proxy)
            #change this to outgoing port
            self.port_ip_association.set(port1, serialized_proxy_info)
            #This is setup in the chrome class to forward traffic to miniproxy
            webdriver = Chrome(port1, remote=True)
            server_thread = threading.Thread(
                target=self.server_loop, 
                args=(port1, outgoing_port,)
            )

            server_thread.daemon = True  # Set as a daemon thread so it will exit when the main program exits
            server_thread.start()

            webdriver_instance = webdriver.get_driver()
            return webdriver_instance
        except redis.RedisError as e:
            print(f"Redis Error: {e}")