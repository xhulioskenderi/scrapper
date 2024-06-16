import socket
import select
import sys
import threading
import socks  # PySocks

def forward_data(src, dst):
    try:
        while True:
            r, w, e = select.select([src, dst], [], [])
            if src in r:
                data = src.recv(4096)
                if len(data) == 0:
                    break
                dst.send(data)
            if dst in r:
                data = dst.recv(4096)
                if len(data) == 0:
                    break
                src.send(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        src.close()
        dst.close()

def extract_connect_host(data):
    lines = data.split("\n")
    for line in lines:
        if line.startswith("CONNECT"):
            host_and_port = line.split(" ")[1]
            host, port = host_and_port.split(":")
            return host, int(port)
    return None, None

def handle_client(client_socket):
    data = client_socket.recv(4096)
    host, port = extract_connect_host(data.decode("utf-8"))

    if host and port:
        # Create a socket object for the SOCKS5 connection
        socks_socket = socks.socksocket()
        
        # Replace with your SOCKS5 proxy details, and include the username and password
        socks_socket.set_proxy(socks.SOCKS5, "45.94.47.66", 8110, username="dbrpczyf", password="tm53d0vp7o4p")

        try:
            # Authenticate and establish a SOCKS5 connection to the intended destination
            socks_socket.connect((host, port))

            # Forward the initial CONNECT data and continue with bidirectional forwarding
            socks_socket.send(data)
            
            threading.Thread(target=forward_data, args=(client_socket, socks_socket)).start()
            threading.Thread(target=forward_data, args=(socks_socket, client_socket)).start()
        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            socks_socket.close()
    else:
        print("Invalid or missing CONNECT request")
        client_socket.close()

if __name__ == "__main__":
    # Create a server socket to accept incoming WebDriver connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 8080))  # Bind to port 8080
    server_socket.listen(5)

    print("Listening for incoming WebDriver connections on port 8080...")
    while True:
        # Wait for a new connection from a WebDriver client
        client_socket, _ = server_socket.accept()

        # Handle the client using a new thread
        threading.Thread(target=handle_client, args=(client_socket,)).start()
