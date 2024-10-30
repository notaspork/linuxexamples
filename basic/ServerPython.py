import socket
import ssl
import threading
import select
import queue
import re
import sys
from concurrent.futures import ThreadPoolExecutor

SERVER_NAME = 'localhost'
SERVER_PORT = 12345
messageCounter = 0
messageCounterLock = threading.Lock()
condition = threading.Condition()

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
        print("Received new connection from ", addr)
        handle_client(conn)

# Threaded mode
def handle_new_connections_threads(sock):
    def handle_client(conn):
        global messageCounter

        while True:
            data = conn.recv(1024)
            if not data:
                break
            print('Received:', data)
            with messageCounterLock:
                nextCount = messageCounter + 1
                threading.Event().wait(0.1)
                messageCounter = nextCount
                if messageCounter == 100:
                    with condition:
                        condition.notify_all()
            print('Total messages received:', messageCounter)
            conn.sendall(data)
        conn.close()

    def notify_100():
        with condition:
            condition.wait()
            if messageCounter >= 100:
                print('*** 100 messages received ***')
            else:
                print('Error: notify_100() called before 100 messages received')

    notifyThread = threading.Thread(target=notify_100)
    notifyThread.start()

    while True:
        conn, addr = sock.accept()
        print("Received new connection from ", addr)
        # conn = setup_ssl(conn)
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()

# Select mode
def handle_new_connections_select(sock):
    global messageCounter

    inputs = [sock]
    outputs = []
    message_queues = {}

    while inputs:
        # The select.select() function blocks until at least one of the input or output sockets is ready for I/O or encounters an exception.
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        
        # Alternatively, we could use the multi-dimensional array form of the result of select.select():
        # results = select.select(inputs, outputs, inputs)
        # readable = results[0]
        # writable = results[1]
        # exceptional = results[2]
        for s in readable:
            if s is sock:
                conn, addr = s.accept()
                print("Received new connection from ", addr)
                # conn = setup_ssl(conn)
                inputs.append(conn)
                message_queues[conn] = queue.Queue()
            else:
                data = s.recv(1024)
                if data:
                    print('Received:', data)
                    nextCount = messageCounter + 1
                    messageCounter = nextCount
                    print('Total messages received:', messageCounter)
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
    global messageCounter

    message_queues = {}
    fd_to_socket = {sock.fileno(): sock}
    timeout = 1000

    poller = select.poll()
    poller.register(sock, select.POLLIN)

    while True:
        events = poller.poll(timeout)
        for fd, flag in events:
            s = fd_to_socket[fd]

            if flag & (select.POLLIN | select.POLLPRI):
                if s is sock:
                    conn, addr = s.accept()
                    print("Received new connection from ", addr)
                    # conn = setup_ssl(conn)
                    fd_to_socket[conn.fileno()] = conn
                    poller.register(conn, select.POLLIN)
                    message_queues[conn] = queue.Queue()
                else:
                    data = s.recv(1024)
                    if data:
                        print('Received:', data)
                        nextCount = messageCounter + 1
                        messageCounter = nextCount
                        print('Total messages received:', messageCounter)
                        message_queues[s].put(data)
                        poller.modify(s, select.POLLIN | select.POLLOUT)
                    else:
                        poller.unregister(s)
                        s.close()
                        del message_queues[s]
            if flag & select.POLLOUT:
                try:
                    next_msg = message_queues[s].get_nowait()
                except queue.Empty:
                    poller.modify(s, select.POLLIN)
                else:
                    s.send(next_msg)
            if flag & select.POLLERR:
                poller.unregister(s)
                s.close()
                del message_queues[s]

# Thread-pool mode
def handle_new_connections_thread_pool(sock):
    global messageCounter

    def handle_client(conn):

        while True:
            data = conn.recv(1024)
            if not data:
                break
            print('Received:', data)
            messageCounter.append(data)
            print('Total messages received:', len(messageCounter))
            conn.sendall(data)
        conn.close()
   
    messageCounter = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        try:
            while True:
                conn, addr = sock.accept()
                print("Received new connection from ", addr)
                # conn = setup_ssl(conn)
                pool.submit(handle_client, conn)
        except:
            print("Shutting down gracefully...")

def initialize_server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_NAME, SERVER_PORT))
    sock.listen(5)
    return sock

# Start the server
def start_server():
    listen_socket = initialize_server_socket()
    # handle_new_connections_simple(listen_socket)
    # handle_new_connections_threads(listen_socket)
    # handle_new_connections_select(listen_socket)
    # handle_new_connections_poll(listen_socket)
    handle_new_connections_thread_pool(listen_socket)

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

# SERVER_NAME = socket.gethostname()
SERVER_PORT = parse_command_line_arguments()
print(f"Starting server on '{SERVER_NAME}' port {SERVER_PORT}")
start_server()
