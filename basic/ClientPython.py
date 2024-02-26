import socket
import ssl

SERVER_NAME = 'localhost'
SERVER_PORT = 12345

class HashTable:
    def __init__(self, buckets):
        self.table = [None] * buckets

    def hash(self, key):
        # return hash of key
        return hash(key) % len(self.table)

    def insert(self, key, value):
        # insert value into table based on key, handling any collisions without losing data
        if (self.table[self.hash(key)] == None):
            self.table[self.hash(key)] = [(key,value)]
        else:
            # check if key already exists
            for k,v in self.table[self.hash(key)]:
                if k == key:
                    # key already exists, replace value
                    v = value
                    return
            self.table[self.hash(key)].append((key,value))
        
    def remove(self, key):
        # remove first value from table that matches key
        l = self.table[self.hash(key)]
        if l == None:
            return
        else:
            for k,v in l:
                if k == key:
                    l.remove((k,v))
                    return

    def get(self, key):
        # return value from table based on key, or None if it is not found
        l = self.table[self.hash(key)]
        if l == None:
            return None
        else:
            for k,v in l:
                if k == key:
                    return v
            return None
        
    def getnthitem(self, n):
        # return nth item in table
        count = 0
        for l in self.table:
            if l != None:
                for k,v in l:
                    if count == n:
                        return (k,v)
                    else:
                        count += 1
        
    def __len__(self):
        # count number of items in table
        count = 0
        for l in self.table:
            if l != None:
                count += len(l)

    def clear(self, buckets):
        self.table = [None] * buckets

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        # add item to stack
        self.stack.append(item)

    def pop(self):
        # remove last item from stack
        self.stack.pop()

    def popMany(self, n):
        # remove last n items from stack
        result = self.stack[-n:]
        del self.stack[-n:]
        return(result)
        
    def __len__(self):
        return len(self.stack)

    def clear(self):
        self.stack = []

class PriorityQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, item, priority):
        # insert item in priority queue based on priority
        # higher priority number = higher priority
        # if priority is same, then FIFO
        # if priority is different, then insert in order
        i = 0
        while (i < len(self.queue)) and (priority <= self.queue[i][1]):
            i += 1
        self.queue.insert(i, (item, priority))
        
    def dequeue(self):
        # remove item with highest priority from priority queue
        return self.queue.pop(0)

    def __len__(self):
        return len(self.queue)
    
    def clear(self):
        self.queue = []

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
            'name': 'Chicken',
            'price': 8.49,
            'transactionType': 100,
            'transactionTime': 100
        },
        {
            'name': 'Milk',
            'price': 2.99,
            'transactionType': 100,
            'transactionTime': 100
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
