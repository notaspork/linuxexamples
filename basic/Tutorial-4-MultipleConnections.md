# Handling Multiple Simultaneous Connections
Reference source file: `ServerPython.py`

## Multiple Simultaneous Connections Introduction
Most real-world servers need to be able to handle many different clients connecting at the same time. Let's try testing 2 connections at once with our server. This is hard since the client finishes and exits so quickly. One option would be to put a delay into the client program to make it easier. However, an easier choice is to just use `nc` again to connect.

First, let's start the server, as before:
```bash
python3 ServerPython.py
```
ServerPython Output:
```
Starting server on 'localhost' port 12345
```
In another tab/window/terminal, start a simulated client using `nc`:
```bash
nc 127.0.0.1 12345
```
ServerPython Output:
```
Received new connection from  ('127.0.0.1', 49743)
```
The server correctly accepts the incoming connection from `nc` and prints its IP address and port. In this case, `nc` is running on the same local host loopback address as the server, and a high-number ephemeral port. Again, your output will probably show a different port number than the above example, since these ports are generated dynamically and can take different values. Note that you can pass `localhost` as the network address or `127.0.0.1` and it will have the same result. `socket.connect()` and similar calls will automatically resolve the domain names such as `localhost` to the proper IP address (in this case `127.0.0.1`).

Next, let's type some input into `nc` to send to the server:
```bash
Hello
```
You should see the following:

ServerPython Output:
```
Received: b'Hello\n'
```
The server correctly prints out the data received, before sending it back to the client over the socket.
`nc` Output:
```
Hello
Hello
```
The `nc` program shows what we typed and sent to the server, followed by the message we received back from the server (which is the same as what we typed in `nc`).

So far so good. We did all this before in an earlier example. However, this time instead of closing `nc`'s connection, let's try adding an additional client while the `nc` "client" is still connected to the server.

In another tab/window/terminal, launch the client:
```bash
python3 ClientPython.py
```
Note that ServerPython will not output anything. It is still handling the connection from `nc`, so it will not accept a new connection until the original one is terminated.

If we kill the `nc` program, we will then see the expected output on the server, as the new ClientPython connection is allowed to connect after `nc`'s connection is terminated:

ServerPython Output:
```
Received new connection from  ('127.0.0.1', 64073)
Received: b'Hello, world'
```
So how do we fix this? While handling one connection at a time makes thing simpler, a server isn't very useful for most real-world situations if it can only handle one client connecting at a time and it makes all other clients wait. Imagine if Google did this; it could take hours or even days for it to be our turn to perform a search.

There are several ways to solve this problem. One of the more straightforward solutions in Python is to use threads.

## Multithreading
In Python, threading allows for the execution of multiple operations at once within a single process.

A thread is a separate flow of execution. This means that your program will have two or more things happening at once. For most Python implementations, the different threads do not actually execute at the same time, they merely appear to, and the computer is actually rapidly switching between executing the different threads. Some operating system-level thread implementations will instead offload each thread onto a separate core on a multicore processor, which means the threads are truly executing at the same time on different cores of the processor.

Threads are lighter in terms of resource usage than processes, and share the same memory space, which facilitates data sharing. This can lead to problems due to simultaneous access of data (known as a race condition). To prevent race conditions, threading provides a number of synchronization primitives including locks, condition variables, and others which will be discussed later.

For now, let's define a new function to replace `handle_new_connections_simple()` with a version using threads:
```python
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
        print("Received new connection from ", addr)
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()
```
This function is almost identical to the `handle_new_connections_simple()` version, except we replaced the final line that called `handle_client(conn)` with 2 lines involving threads.

The first of these uses the `threading` module member function `.Thread()` to create a new thread and stores the result in a new local variable we call, appropriately enough, `thread`. `threading.Thread()` can take many arguments to specify particular thread attributes and behavior, but we only care about 2 of them, so we specify the names of the parameters we care about, `target` and `args`. The `target` parameter to `threading.Thread()` specifies the function that the thread will execute when started, in this case `handle_client()`. By default, Python threads will not start execution until you call their `.start()` method function, which occurs on the following line. Since a Python thread is also an object, it contains many useful member functions like `.start()`.

We also specify the `args` parameter to `threading.Thread()`, which is a *tuple* that contains the arguments to the `handle_client()` function we specified as the `target` parameter. It could be empty (or we could just leave out the parameter) if `handle_client()` had no arguments. However, `handle_client()` has exactly one argument. Because of this, instead of providing the parameter `args=(conn)`, which the Python interpreter would internally simplify to `args=conn` like it normally does with parentheses, we need to put at least one comma in the parentheses to show Python that it is a *tuple*, so we write `args=(conn,)`. While this may look a bit strange, we are essentially saying that this is a *tuple* with only one element (the second element is blank/non-existent, so there is nothing after the comma). This forces Python to keep this parameter as a *tuple*, which then has its elements mapped to the parameters of `handle_client()`. If we instead just passed `conn` directly without a *tuple*, the program would fail because Python does not know how to map a *socket* object to the parameters of a function, only how to map *tuples* to function parameter lists.

Looking again at the above code, `handle_new_connections_threads()` will loop forever `while True`, calling `sock.accept()` to wait for a new incoming connection each time, just as before. The difference is that `handle_new_connections_simple()` would immediately handle each new incoming connection by calling `handle_client()` directly, which blocked any additional connections until `handle_client()` returned. Instead, `handle_new_connections_threads()` creates and then starts a new *thread* for *each* new incoming connection, which takes almost no time at all, then goes back to listening for more new connections by calling `sock.accept()` again at the next iteration through the `while` loop. Meanwhile, *each* newly created *thread* in turn calls `handle_client()` for that thread's incoming connection, allowing both the main (listening) thread and all the threads created for each successive incoming connection to all run *at approximately the same time*. There is no noticeable delay in this process, so nobody has to really wait on anyone else. This allows the threaded version of the server to handle many clients all at once, instead of one at a time.

Note that `handle_client()` is a *local* function to the new `handle_new_connections_threads()` function. The old `handle_new_connections_simple()` function also has its own *local* `handle_client()` function. While in this case the code for both functions is identical, each `handle_new_connections_` function calls its own *local* version of `handle_client()`. This allows each one to be customized for its particular use case, despite them both having the same name. If we wanted to, we could instead remove these 2 *local* `handle_client()` functions and have a *global* `handle_client()` function instead in the main body of the code. In that case, every function that called `handle_client()` would be calling the same code, and there would only be one version of the function to maintain.

Finally, we need to change the `start_server()` function to call `handle_new_connections_threads()` instead of `handle_new_connections_simple()`:
```python
def start_server():
    listen_socket = initialize_server_socket()
    # handle_new_connections_simple(listen_socket)
    handle_new_connections_threads(listen_socket)
```
Rather than just changing the function name, we will comment the old line out and add a new one. This way, we can easily switch back between non-threaded and threaded modes for testing.

Now, let's try running the revised server program:
```bash
python3 ServerPython.py
```
ServerPython Output:
```
Starting server on 'localhost' port 12345
```
In another tab/window/terminal, again start a simulated client using `nc`:
```bash
nc 127.0.0.1 12345
```
ServerPython Output:
```
Received new connection from  ('127.0.0.1', 49743)
```
Next, let's type some input into `nc` to send to the server:
```bash
Hello
```
ServerPython Output:
```
Received: b'Hello\n'
```
Now, in another tab/window/terminal, start the client:
```bash
python3 ClientPython.py
```
ServerPython Output:
```
Received new connection from  ('127.0.0.1', 64073)
Received: b'Hello, world'
```
ClientPython Output:
```
Starting client...
Received: b'Hello, world'
```
Even though the `nc` "client" is still connected to the server, the server properly handles the ClientPython program's connection, echos back the data, and ClientPython completes and exits, all while `nc` is still connected to the server.

To validate that `nc` is still connected, we can send additional data through `nc`'s connection by typing additional lines into the `nc` program:
```
Still here!
```
ServerPython Output:
```
Received: b'Still here!\n'
```
Note that the server does not show any new connections occurring, it simply prints the message we just sent from `nc`, showing that `nc` was still connected to the server the entire time.
