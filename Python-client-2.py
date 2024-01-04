import socket
import ssl

SERVER_NAME = 'localhost'
SERVER_PORT = 12345

class BinarySearchTree:

    key = None
    value = None
    left = None
    right = None

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def insert(self, key, value):
        if key < self.key:
            if self.left == None:
                self.left = BinarySearchTree(key, value)
            else:
                self.left.insert(key, value)
        elif key > self.key:
            if self.right == None:
                self.right = BinarySearchTree(key, value)
            else:
                self.right.insert(key, value)
        else:
            self.value = value

    def get(self, key):
        if key < self.key:
            if self.left == None:
                return None
            else:
                return self.left.get(key)
        elif key > self.key:
            if self.right == None:
                return None
            else:
                return self.right.get(key)
        else:
            return self.value
    
    # fix this and add balance, clear
    @staticmethod
    def remove(tree, key):
        if tree == None:
            return None
        elif key < tree.key:
            tree.left = BinarySearchTree.remove(tree.left, key)
            return tree
        elif key > tree.key:
            tree.right = BinarySearchTree.remove(tree.right, key)
            return tree
        elif tree.left == None:
            return tree.right
        elif tree.right == None:
            return tree.left
        else:
            # find smallest key in right subtree
            smallest = tree.right
            while smallest.left != None:
                smallest = smallest.left
            # replace current key with smallest key
            tree.key = smallest.key
            tree.value = smallest.value
            # remove smallest key from right subtree
            tree.right = BinarySearchTree.remove(tree.right, smallest.key)
            return tree

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

def start_client():
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect(('localhost', 12345))
    with socket.create_connection((SERVER_NAME, SERVER_PORT)) as sock:
        #with create_ssl_socket(sock) as ssock: (also change sock to ssock below)
        send_data_simple(sock)
        receive_data_simple(sock)
    # sock.close()

def send_data_simple(sock):
    sock.sendall(b'Hello, world')

def receive_data_simple(sock):
    data = sock.recv(1024)
    print('Received:', data)

def create_ssl_socket(sock):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context.wrap_socket(sock, server_hostname=SERVER_NAME)

def send_data_simple_udp(sock):
    sock.sendto(b'Hello, world', (SERVER_NAME, SERVER_PORT))

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
    return sorted(tList, key=lambda t: t['price'])

def compute_average_price(transactions):
    return sum([t['price'] for t in transactions]) / len(transactions)

print('Starting client...')
start_client()
