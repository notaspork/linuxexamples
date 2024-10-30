import socket
import ssl

SERVER_NAME = 'localhost'
SERVER_PORT = 12345

def create_ssl_socket(sock):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context.wrap_socket(sock, server_hostname=SERVER_NAME)

def send_data_simple_udp(sock):
    sock.sendto(b'Hello, world', (SERVER_NAME, SERVER_PORT))

def receive_data_simple_udp(sock):
    data, address = sock.recvfrom(1024)
    print('Received (from {}):'.format(address), data)

def send_data_simple(sock):
    sock.sendall(b'Hello, world')

def receive_data_simple(sock):
    data = sock.recv(1024)
    print('Received:', data)

def start_client_simple():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 12345))
    send_data_simple(sock)
    receive_data_simple(sock)
    sock.close()

def start_client_simple_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_data_simple_udp(sock)
    receive_data_simple_udp(sock)
    sock.close()

def start_client():
    with socket.create_connection((SERVER_NAME, SERVER_PORT)) as sock:
        #with create_ssl_socket(sock) as ssock: (also change sock to ssock below)
        send_data_simple(sock)
        receive_data_simple(sock)
    
def create_example_transactions():
    return [
        {
            'username': 'Alice',
            'IP': "10.0.0.9",
            'port': 54362,
            'accessTime': 100,
            'dataSent' : 100,
            'score' : 1.0
        },
        {
            'username': 'Bob',
            'IP': "10.0.0.4",
            'port': 24153,
            'accessTime': 100,
            'dataSent' : 100,
            'score' : 1.0
        }
    ]

def sort_by_price(tList):
    def get_price(t):
        return t['price']
    return sorted(tList, key=get_price)

def compute_average_price(transactions):
    return sum([t['price'] for t in transactions]) / len(transactions)

print('Starting client...')
start_client_simple()
