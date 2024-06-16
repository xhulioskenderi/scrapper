import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from socket import SOL_SOCKET, SO_KEEPALIVE, SO_REUSEADDR
from threading import Thread

logging.basicConfig(level=logging.DEBUG)

class MyHTTPServer(HTTPServer):
    def server_bind(self):
        super().server_bind()
        self.socket.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        logging.info(f"Server bound to port {self.server_address[1]} with SO_KEEPALIVE and SO_REUSEADDR options set.")

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info("Received GET request.")
        self.send_response(200)  # Status code: 200 OK
        self.send_header("Content-Type", "text/plain")  # Content type
        self.send_header("Connection", "keep-alive")  # Keep-Alive!
        self.end_headers()
        self.wfile.write(b'HTTP')  # Actual response body
        logging.info("Response sent.")

def run_server(port):
    server_address = ('', port)
    httpd = MyHTTPServer(server_address, SimpleHTTPRequestHandler)
    logging.info(f"Starting server on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    ports = [8111, 8112, 8113]  # Replace with your desired ports
    threads = []

    for port in ports:
        thread = Thread(target=run_server, args=(port,))
        thread.start()
        threads.append(thread)
        logging.info(f"Thread started for port {port}")

    for thread in threads:
        thread.join()
