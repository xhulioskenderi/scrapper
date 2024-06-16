import socket
import threading
import logging
import signal
# Initialize logging
logging.basicConfig(level=logging.INFO)


#Add fetching the port numbers in the init or maybe fetch them elsewhere so you can combine them with a uuid

class MiniProxy:

    backend_servers = ["http://localhost:8001", "http://localhost:8002", "http://localhost:8003"]

    def __init__(self, port1, port2, website):
        self.shutdown_flag = False
        self.port1 = port1
        self.port2 = port2
        self.website = website
        signal.signal(signal.SIGTERM, self.signal_handler)
        logging.info("MiniProxy initialized")
    

    def signal_handler(self, signum, frame):
        logging.info("Signal received, shutting down...")
        self.shutdown_flag = True

    #Create and keep socket open to listen for shutdown flag.
    def handle_control_connection(self, control_socket):
        logging.info("Control connection handler started")
        while True:
            command = control_socket.recv(1024).decode('utf-8')
            if command == "SHUTDOWN":
                logging.info("Shutdown command received from control socket.")
                self.shutdown_flag = True
                break
            else:
                logging.info(f"Unknown command received: {command}")

    '''
    This mini proxy will route it's traffic to the socks5 proxy server target_host and target_port need to be 
    the ones where the Socsks5 proxy server is running.
    '''
    def handle_client(self, client_socket):
        logging.info("Client handler started")
        target_host = 'localhost'
        #Remember to put the socks5 proxy port down here
        target_port = 8001
        min_buffer_size = 1024
        max_buffer_size = 8192
        buffer_size = 4096

        total_received = 0
        packet_count = 0
        avg_packet_size = 0


        try:
            # Connect to the target
            target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target.connect((target_host, target_port))
            logging.info(f"Connected to target {target_host}:{target_port}")
        except Exception as e:
            logging.error(f"Could not connect to target: {e}")
            client_socket.close()
            return

        while True:
            #Remember to add information in the logs to identify the website 
            if self.shutdown_flag:
                logging.info("Shutdown flag set, closing sockets")
                client_socket.close()
                target.close()
                break

            try:
                # Receive data from client
                client_data = client_socket.recv(buffer_size)
                packet_size = len(client_data)
                logging.debug(f"Received {packet_size} bytes from client")
                total_received += packet_size  # Update total_received
                packet_count += 1  # Update packet_count
                avg_packet_size = total_received / packet_count  # Compute average packet size


                # Adapt buffer size
                if avg_packet_size > buffer_size * 1.5 and buffer_size < max_buffer_size:
                    buffer_size = min(max_buffer_size, buffer_size * 2)
                    logging.info(f"Increasing buffer size to {buffer_size}")

                elif avg_packet_size < buffer_size * 0.5 and buffer_size > min_buffer_size:
                    buffer_size = max(min_buffer_size, buffer_size // 2)
                    logging.info(f"Decreasing buffer size to {buffer_size}")


                if not client_data:
                    logging.info("Client disconnected")
                    break

                # Send it to target
                target.send(client_data)
                # Receive response from target
                target_data = target.recv(buffer_size)
                logging.debug(f"Received {len(target_data)} bytes from target")


                if not target_data:
                    logging.info("Target disconnected")
                    break

                # Send response back to client
                client_socket.send(target_data)

            except Exception as e:
                logging.error(f"Error while forwarding data: {e}")
                break

        # Close the sockets
        client_socket.close()
        target.close()

#build a pool to pull threads from 

    def server_loop(self):
        host = "0.0.0.0"  # Listen on all interfaces


        #Server socket for client connection. This is where the webdriver traffic will be forwarded to as specified in the Chrome class 
        #of the browser_setup_code.py file 
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, self.port1))
        server.listen(5)
        logging.info(f"Server listening on {host}:{self.port1}")

        #Server socket for control connections

        control_host = 'localhost'
        control_port = self.port2
        control_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_server.bind((control_host, control_port))
        control_server.listen(1)
        logging.info(f'Control socket listening on {control_host}:{control_port} for {self.website}')

        #Start control thread

        control_socket, _ = control_server.accept()
        control_thread = threading.Thread(target=self.handle_control_connection, args=(control_socket,))
        control_thread.start()


        while True:
            if self.shutdown_flag:
                logging.info("Shutdown flag set, shutting down server.")
                server.close()
                control_server.close()
                break


            try:
                client_socket, addr = server.accept()
                logging.info(f"Accepted connection from {addr[0]}:{addr[1]}")

                # Spin up a thread to handle the client
                client_thread = threading.Thread(target= self.handle_client , args=(client_socket,))
                client_thread.start()
            except Exception as e:
                logging.error(f"Error while accepting connection: {e}")


if __name__ == "__main__":
    # Instantiate your class
    mini_proxy = MiniProxy(8111, 8112, 'https://example.com')
