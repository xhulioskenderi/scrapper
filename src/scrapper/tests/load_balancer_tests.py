import socket
import time

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port

def mock_client(load_balancer_port, source_port, num_requests=5):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.bind(('0.0.0.0', source_port))
        client_socket.connect(('localhost', load_balancer_port))

        for i in range(num_requests):
            client_socket.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            data = client_socket.recv(1024)
            print(f"Request-{i} received: {data.decode()}")
            time.sleep(1)

    except Exception as e:
        print(f"[ERROR] Could not connect to port {load_balancer_port}: {e}")
    finally:
        client_socket.close()
        time.sleep(50)

if __name__ == "__main__":
    load_balancer_port = 9001
    source_port1 = find_free_port()  # Find a free port
    source_port2 = find_free_port()

    while source_port1 == source_port2:
        source_port2 = find_free_port()

    for _ in range(5):  # Repeat the whole operation 5 times
        mock_client(load_balancer_port, source_port1)
        print(f"Client interaction from port {source_port1} complete.")
        time.sleep(5)
        
        mock_client(load_balancer_port, source_port2)
        print(f"Client interaction from port {source_port2} complete.")
        time.sleep(5)