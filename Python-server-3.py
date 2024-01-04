import socket
import ssl
import threading
import select
import queue
import re
import sys

SERVER_NAME = 'localhost'
SERVER_PORT = 12345

class SSLContextSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            cls._instance.context.load_cert_chain(certfile="server.crt", keyfile="server.key")
        return cls._instance

def setup_ssl_singleton(sock):
    ssl_context = SSLContextSingleton()
    return ssl_context.context.wrap_socket(sock, server_side=True)


def setup_ssl(sock):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    return context.wrap_socket(sock, server_side=True)

# Simple single-client non-threaded mode
def handle_new_connections_simple(sock):

    def handle_client(conn):
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print('Received:', data)
            conn.sendall(data)
        conn.close()

    while True:
        conn, addr = sock.accept()
        handle_client(conn)

# Threaded mode
def handle_new_connections_threads(sock):

    def handle_client(conn):
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print('Received:', data)
            conn.sendall(data)
        conn.close()

    while True:
        conn, addr = sock.accept()
        # conn = setup_ssl(conn)
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()

# Select mode
def handle_new_connections_select(sock):
    inputs = [sock]
    outputs = []
    message_queues = {}

    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for s in readable:
            if s is sock:
                conn, addr = s.accept()
                # conn = setup_ssl(conn)
                inputs.append(conn)
                message_queues[conn] = queue.Queue()
            else:
                data = s.recv(1024)
                if data:
                    print('Received:', data)
                    message_queues[s].put(data)
                    if s not in outputs:
                        outputs.append(s)
                else:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    del message_queues[s]

        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except queue.Empty:
                outputs.remove(s)
            else:
                s.send(next_msg)

        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del message_queues[s]

# Poll mode
def handle_new_connections_poll(sock):
    message_queues = {}
    fd_to_socket = {sock.fileno(): sock}
    timeout = 1000

    poller = select.poll()
    poller.register(sock, select.POLLIN)

    while True:
        events = poller.poll(timeout)
        for fd, flag in events:
            s = fd_to_socket[fd]
            print(s)
            if flag & (select.POLLIN | select.POLLPRI):
                if s is sock:
                    conn, addr = s.accept()
                    # conn = setup_ssl(conn)
                    fd_to_socket[conn.fileno()] = conn
                    poller.register(conn, select.POLLIN)
                    message_queues[conn] = queue.Queue()
                else:
                    data = s.recv(1024)
                    if data:
                        print('Received:', data)
                        s.send(data)
                    else:
                        poller.unregister(s)
                        s.close()

def initialize_server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_NAME, SERVER_PORT))
    sock.listen(5)
    return sock

# Start the server
def start_server():

    listen_socket = initialize_server_socket()
    # handle_new_connections_simple(listen_socket)
    handle_new_connections_threads(listen_socket)
    # handle_new_connections_select(listen_socket)
    # handle_new_connections_poll(listen_socket)

def parse_command_line_arguments():
    port = SERVER_PORT

    # Check if -p parameter is provided
    if '-p' in sys.argv:
        index = sys.argv.index('-p')
        if index + 1 < len(sys.argv):
            port = int(sys.argv[index + 1])

    # Check if --port= parameter is provided
    for arg in sys.argv:
        match = re.match(r'--port=(\d+)', arg)
        if match:
            port = int(match.group(1))

    return port

SERVER_PORT = parse_command_line_arguments()
print('Starting server on port', SERVER_PORT)
start_server()

# TODO: locks, condition vairables, atomics, thread pool (with graceful shutdown without memory leaks)
# sendto, recvfrom, connect, gethostname

# unit tests in client?