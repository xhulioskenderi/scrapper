import socket
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        a = s.getsockname()[1]
        print(a)

find_free_port()