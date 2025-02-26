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

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        # add item to stack
        self.stack.append(item)

    def pop(self):
        # remove last item from stack
        return self.stack.pop()

    def popMany(self, n):
        # remove last n items from stack
        result = self.stack[-n:]
        del self.stack[-n:]
        return(result)
        
    def __len__(self):
        return len(self.stack)

    def clear(self):
        self.stack = []

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
        return None
        
    def __len__(self):
        # count number of items in table
        count = 0
        for l in self.table:
            if l != None:
                count += len(l)
        return count

    def clear(self, buckets):
        self.table = [None] * buckets

## Unit Testing code begins here
import unittest

class TestHashTable(unittest.TestCase):
    def test_insert_and_get(self):
        # Test inserting values into the hash table and retrieving them
        hash_table = HashTable(buckets=10)
        hash_table.insert("key1", "value1")
        hash_table.insert("key2", "value2")
        self.assertEqual(hash_table.get("key1"), "value1")
        self.assertEqual(hash_table.get("key2"), "value2")

    def test_collision_handling(self):
        # Test handling collisions in the hash table
        hash_table = HashTable(buckets=1)
        hash_table.insert("key1", "value1")
        hash_table.insert("key2", "value2")
        # Ensure that both values are stored despite the hash collision
        self.assertEqual(hash_table.get("key1"), "value1")
        self.assertEqual(hash_table.get("key2"), "value2")

    def test_remove(self):
        # Test removing a key from the hash table
        hash_table = HashTable(buckets=10)
        hash_table.insert("key1", "value1")
        hash_table.remove("key1")
        self.assertIsNone(hash_table.get("key1"))

    def test_getnthitem(self):
        # Test retrieving the nth item from the hash table
        hash_table = HashTable(buckets=10)
        hash_table.insert("key1", "value1")
        hash_table.insert("key2", "value2")
        item0 = hash_table.getnthitem(0)
        item1 = hash_table.getnthitem(1)
        self.assertTrue((item0 == ("key1", "value1")) and (item1 == ("key2", "value2")) or (item1 == ("key1", "value1")) and (item0 == ("key2", "value2")))
        # self.assertEqual(hash_table.getnthitem(0), ("key1", "value1"))
        # self.assertEqual(hash_table.getnthitem(1), ("key2", "value2"))
        self.assertIsNone(hash_table.getnthitem(-1))
        self.assertIsNone(hash_table.getnthitem(2))

    def test_clear(self):
        # Test clearing the hash table
        hash_table = HashTable(buckets=10)
        hash_table.insert("key1", "value1")
        hash_table.clear(5)
        self.assertIsNone(hash_table.get("key1"))

class TestStack(unittest.TestCase):
    def test_push_and_pop(self):
        # Test pushing and popping items from the stack
        stack = Stack()
        stack.push("item1")
        stack.push("item2")
        self.assertEqual(stack.pop(), "item2")

    def test_popMany(self):
        # Test popping multiple items from the stack
        stack = Stack()
        stack.push("item1")
        stack.push("item2")
        stack.push("item3")
        self.assertEqual(stack.popMany(2), ["item2", "item3"])

    def test_clear(self):
        # Test clearing the stack
        stack = Stack()
        stack.push("item1")
        stack.clear()
        self.assertEqual(len(stack), 0)

class TestPriorityQueue(unittest.TestCase):
    def test_enqueue_and_dequeue(self):
        # Test enqueuing and dequeuing items from the priority queue
        priority_queue = PriorityQueue()
        priority_queue.enqueue("item1", 2)
        priority_queue.enqueue("item2", 1)
        priority_queue.enqueue("item3", 2)
        self.assertEqual(priority_queue.dequeue(), ("item1", 2))
        self.assertEqual(priority_queue.dequeue(), ("item3", 2))
        self.assertEqual(priority_queue.dequeue(), ("item2", 1))

    def test_clear(self):
        # Test clearing the priority queue
        priority_queue = PriorityQueue()
        priority_queue.enqueue("item1", 2)
        priority_queue.clear()
        self.assertEqual(len(priority_queue), 0)

if __name__ == '__main__':
    unittest.main()
