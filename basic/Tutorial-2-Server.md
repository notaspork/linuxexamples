# Python Server
Reference source file: `ServerPython.py`

## Python Server Introduction
For this lesson, we are going to write a networked server in Python. We will start with something simple and build it up from there. It is recommended that you do this in non-interactive mode, incrementally creating a `ServerPython.py` file from scratch as part of following along in this tutorial. If you attempt to simply follow along on the pre-created source file, you may have a hard time identifying which parts of the file correspond to which stages of the tutorial.

## main code
We will begin by writing the core code. In order to more easily be able to change these values as needed, we will use variables to represent the network name of the server `SERVER_NAME` and the port to listen for client connections on `SERVER_PORT`.
```python
SERVER_NAME = 'localhost'
SERVER_PORT = 12345
```
Initially, we will be running the client and server both locally for ease of testing during the early development process, so we set `SERVER_NAME` to `'localhost'` and pick port 12345 to use for `SERVER_PORT`. These can be changed in the future if you wish to use a different address/port.

```python
print('Starting server on port', SERVER_PORT)
```
Next we print out a message to let us know the server is starting and remind us of what port it is on.

```python
start_server()
```
To make the organization of our program easier, we are going to encapsulate the main server code itself in a function called `start_server`. We now have to define this function:

```python
def start_server():
    listen_socket = initialize_server_socket()
    handle_new_connections_simple(listen_socket)
```
To define a new function, we 
Because this function is really just to organize our code, it doesn't need any arguments. We're going to break down the operations of the server into two main phases-- setting up, and handling new connections. We will call `initialize_server_socket` to obtain a new socket that will listen for incoming connections. We then pass this new `listen_socket` as an argument to the function `handle_new_connections_simple`, which will listen on that socket for any incoming connections, and process them appropriately. Neither of these are existing Python functions-- they are both functions we made up that we will therefore have to define and implement.

## Creating a listening socket
Let's start with defining `initialize_server_socket`:
```python
def initialize_server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```
This function does not require any arguments. It first uses the Python `socket` module to request a new socket. The function `socket` is confusingly also the name of a function of the `socket` module itself, which is why it is called as `socket.socket()`. Just as before, we use the `.` symbol to access a function that is part of a larger object. In this case, we are trying to call the `socket()` function contained inside the `socket` module. Normally functions won't have the exact same name as the module that contains them, but `socket` is unfortunately an exception to this general trend.

The `socket.socket()` function takes a few arguments. The first argument specifies what type of network protocol that you want a socket for (the Network Layer in the OSI model). For IPv4, use the value `socket.AF_INET`. For IPv6, you can use the value `socket.AF_INET6`. Some operating systems support other types of network protocols as well. The second argument specifies the type of socket requested within that network protocol (the Transport Layer in the OSI model). In this case, we want a TCP socket, so we use `socket.SOCK_STREAM`. The reason we put the `socket.` in front of all these values is because they are all defined inside of the Python `socket` module, so we need to use the `.` symbol in order to access them inside that module.

Next, we use the `bind` function to bind our new socket to a specific network address and port:
```python
    sock.bind((SERVER_NAME, SERVER_PORT))
```
This line uses the function `bind`, which is a function provided to sockets to be able to attach to a specific network address and port. But why isn't it `socket.bind`, since `bind` is defined as part of the `socket` module? Well, often functions are members of all data variables of a specific type. In Python (and most object-oriented programming languages), data variable types that contain functions or other components that you can access with the `.` symbol are also known as *objects*. In this case, any variable/object that is assigned the value of a socket (such as from the `socket.socket()` function call) will automatically contain functions for operating on that socket. Because these functions are contained in a specific socket `sock`, the `bind` call knows to apply only to the socket `sock`, rather than any other socket.

The other important thing to note here is that there is a single argument to `sock.bind()`. The single argument provided is `(SERVER_NAME, SERVER_PORT)`, which might look like two argument, but it's actually one argument (which is why there are two sets of parentheses after `sock.bind`, rather than one).

In Python, `(item0, item1, item2, etc.)` is used to denote a *tuple*, which is essentially an *immutable* vector containing one or more data items. So `(1, 2, 3)` would be a tuple that contains 3 numbers, and `(SERVER_NAME, SERVER_PORT)` is a tuple that contains 2 variables, `SERVER_NAME` and `SERVER_PORT`. A tuple is treated as a single object, which is why it is the sole argument to `sock.bind()`, despite the fact that the tuple passed as the arugment actually in turn contains 2 different variables.

Finally, we call `sock.listen()` to tell our new socket to listen for incoming connections on the bound port.
```python
    sock.listen(5)
```
Like `bind`, `listen` is a function contained in all socket objects. The argument to `listen` specifies the maximum number of incoming connections to queue at once before refusing new connections (also known as the *backlog*). This line tells Python that if there are already 5 incoming connections waiting to connect to the socket, any additional connections will be refused until that queue is reduced to below 5. If you don't want any incoming connections to wait for the socket to be available, you can pass zero as the argument. Be aware that regardless of what number you specify, the operating system might limit the maximum size of such a backlog queue.

Finally, the function needs to return the newly created and listening socket `sock`.

```python
    return sock
```
Please note that while the `socket` module is provided with pretty much every Python distribution on the planet, it is still not included in your program by default. Attempting to run the above code will result in a Python error such as:
```python
NameError: name 'socket' is not defined
```
In order to prevent this error from occurring, you need to tell Python to include the `socket` module in your program. To do this, at the very top of your Python source code, type:
```python
import socket
```
This will cause Python to include the `socket` module and make it available to your program, to avoid such errors.

## Handling new incoming connections
Again, we will start by defining a function to handle incoming connections:
```python
def handle_new_connections_simple(sock):
```
In this case, our function takes a single argument, `sock`, which specifies the listening socket that we watch for new connections.

*socket* objects provide a function `accept` which can be used to accept new incoming TCP connections. `accept` will block and wait until it receives a new incoming TCP connection. Once such a connection comes in, it will return a new socket created just for that connect, along with the network address that the new connection came from. Our code will loop forever to process every incoming connection, one at a time:
```python
    while True:
        conn, addr = sock.accept()
        print("Received new connection from ", addr)
        handle_client(conn)
```
The `while` keyword creates a loop, similarly to the `for` keyword, except instead of iterating through a list, it will execute the indented code underneath for as long as the condition directly after the word `while` is *True*. In this case, we specify `True` as our `while` condition, so the code will loop, executing the indented code over and over, forever. This is desired because we want our program to continue to accept and process new incoming connections forever, until the program is killed.

The notation `conn, addr = sock.accept()` shows that `sock.accept()` returns not just one argument, but two. By providing multiple variables, separated by commas, we can store the result (the return value) of the function `accept` in a new `conn` variable and a new `addr` variable all at once, with a single line of code.

`conn` contains the new socket created by the `accept` function just for the new incoming connection. This allows the listening socket `sock` to continue listening for and processing additional new connections.

`addr` contains the IP address of the source of the incoming connection. We see this address when it is printed out on the next line of code. The `print` statement there may look slightly different than how we have used `print` before. In this case, we are passing multiple arguments to `print`. This causes print to print each of the arguments, one after another. It does not provide the control and flexibility we get with the `.format` method function, but it can be a quick and easy way to print out a wider variety of data types.

### Nested functions
Finally, we want to actually do something with the new connection we received in `conn`. We are going to write a new function `handle_client` to handle this. Instead of defining a *global* function at the top level of our program, this function will be *local* to the `handle_new_connections_simple` function. This way it will only exist, and can only be accessed, from inside the `handle_new_connections_simple` function, not from anywhere else in the code. This allows us to make our `handle_new_connections_simple` code easier to read by abstracting the handling of new connections away into a sub-function, but to also make it clear that it is associated with `handle_new_connections_simple`, rather than the rest of the program.

Now we need to define the `handle_client` function. This function will watch the new connection for data, print out any data received, then send that same data back to the sender over the network.

We put function this directly underneath the `def handle_new_connections_simple(sock):` line, to indicate it is contained in this function. This is sometimes also referred to as a *nested function*:
```python
    def handle_client(conn):
        while True:
            data = conn.recv(1024)
```
We start with a function definition line as usual, with a single argument `conn` which will be passed the new connection socket returned from the `accept` function. Note that `conn` in `handle_client` is a `conn` variable *local* to the `handle_client` function, and only takes the value passed as an argument to `handle_client`, rather than any `conn` variable that might appear outside of the `handle_client` function. In this case, we actually pass the `conn` variable from the `handle_new_connections_simple` function as the `conn` argument to the `handle_client` function, so they will have the same value for that reason, but it is important to realize that they could be different if `handle_client` was ever called somewhere else, with a different argument passed to it. As you can see, it can sometimes be confusing to name them the same thing in different functions, and you may want to consider picking more unique names for some of your local function variables.

Note that both the `handle_client` function definition and its body of code are all indented by one tab more than normal, since they are inside the `handle_new_connections_simple` function.

### Receiving data
`handle_client` also uses a `while True:` statement to loop forever, so it keeps receiving incoming data as long as it is available. Each pass through the loop, it can receive up to 1024 bytes of incoming data using the `recv` function, which is another method function contained in socket objects. The argument to `recv` is the maximum number of bytes we want to receive at a time, in this case 1024. We could have picked a different number, but too small of a size could make the program less efficient (since we would need a lot more times through the loop to receive the same amount of data), and too large of a size might use too much memory (because Python needs to set aside this many bytes of memory to hold the incoming data), so 1024 is a reasonable value for now. Experimenting with this parameter could allow us to tweak network performance and memory usage further. The result (return value) of the `recv` function is stored in the variable `data`.

If the `recv` function is called after a socket is closed and all data has been received, it will return the special value `None` instead of data. `None` is essential an "empty" variable in Python-- it contains no data. In Python, `None`, `0`, and `False` will all evaluate to `False`, for example in a condition after an `if` or `while` statement. The keyword `not` will negate a `True` or `False` expression. Therefore, `not data` will be `True` if and only if `data` is `False`, `0`, or `None`.
```python
            if not data:
                break
```
The `if` line will check to see if the `data` returned from the `recv` function is empty. If it is, it means the connection has closed and all the outstanding data has been received, and it will execute the command on the indented line: `break`.

### The `break` command
`break` is a special command used to exit the current loop (in this case a `while` loop, but it also works on `for` loops). If you have nested loops (one loop indented inside another), `break` will only exit from the innermost loop it is inside.

In this case, `break` causes the program to stop the `while` loop and continue execution of the code after the `while` loop, when the connection has closed and all the outstanding data has been received.

If `data` is not empty, we will print out the data to the screen, as well as send it back to the sender:
```python
            print('Received:', data)
            conn.sendall(data)
```
`print` allows us to print the `data` returned from the `recv` function. `sendall` is another member function contained in *sockets* that transmits any data passed as its argument through the connected socket. Note that `data` is actually a *bytes* object. This is an *immutable* sequence of characters like a *string*, but it can contain binary data as well as text. We can create our own *bytes* object with `bytes([0, 1, 2])` to specify the bytes contained in its sequence, but we do not have to worry about this here, because `recv` already created the *bytes* object for us.

In the previous `if not data:` line, you might have wondered what would happen if we received a `0` byte over the network, since if `data` is `0` this would cause the `if` condition to be `True`, and the loop to exit. However, because `data` is a *bytes* object, it is not an integer, so will never have a value of `0` itself if it is not empty, even though it might contain 1 or more bytes in its sequence that have a value of `0`. In order words, `data` can contain a `0` without being `0` itself. So we do not need to worry about exiting prematurely just because we receive `0` byte values over the network, because a `0` byte is still a byte of data.

### Closing the socket
Once the `while` loop has been exited, we also need to close the *socket*. To do this, we use the *socket* member function `close`:
```python
        conn.close()
```
It is important to remember to `close` any sockets we create (for example, the ones we created by calling the `socket()` or `accept()` functions), in order to free the resources that both Python and the operating system reserve for each socket. If we do not properly `close` sockets once we are done with them, we may eventually run out of memory or the ability to create or accept new network connections. Failure to `close` a socket also can cause the other side to keep a connection open much longer than it should. For example in our code above, if the incoming connection is not closed by the sender, our code will never exit the loop, and so we will be waiting to receive new data forever (or until the connection times out or our program is killed). 

Note that this line shares the same indentation as the `while` line, so it is not part of the `while` loop, it is only executed after the `while` loop is exited. Since the `while` condition here is always `True`, the loop only exits when the connection is closed and `break` is called.

To see this in context, the entire `handle_new_connections_simple` function in order now looks like this:
```python
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
```

## Testing the server
Now, let's try running this server:
```bash
python3 ServerPython.py
```
Output:
```
Starting server on port 12345
```
So far, so good! The program correctly prints the port it is listening for new connections on.

Let's try to connect to the server. Eventually, we will write another program to be the client, but for testing, we will use the *netcat* program (also called `nc`). `nc` is installed on many operating systems by default, but if it is not, you can download it. In an apt-aware Linux distribution (such as Debian or Ubuntu), you can also install it with `apt-get install netcat`.

Once `nc` is installed, we can use it to connect to our server on port 12345. The first argument to `nc` on the command line is the network address of the host to connect to, and the second argument is the port to connect to. In this case, we use the loopback IP address 127.0.0.1 to specify the local host and port 12345 for our server:
```bash
nc 127.0.0.1 12345
```
ServerPython Output:
```
Received new connection from  ('127.0.0.1', 49743)
```
The server correctly accepts the incoming connection from `nc` and prints its IP address and port. In this case, `nc` is running on the same local host loopback address as the server, and a high-number ephemeral port. Your output will probably show a different port number than the above example, since these ports are generated dynamically and can take different values.

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

You can send more data to experiment further, or press Ctrl-C to kill the `nc` program. You can also instead press Ctrl-D in `nc` at the input prompt, which will send an End-of-File (EOF) message, indicating that no more data exists from the client side of the connection, and will cleanly close the socket. Because the server program does not accept user input, you will need to use Ctrl-C to kill the server. We will discuss this distinction in more detail later.

## SSL setup
TBD:

To create a server.crt (certificate) and server.key (private key) file, you can use OpenSSL, a widely used software library for applications that secure communications over computer networks. Here are the steps:

Generate a private key:

```bash
openssl genrsa -out server.key 2048
```

This command generates a 2048-bit RSA private key and writes it to a file named server.key.

Generate a Certificate Signing Request (CSR):

```bash
openssl req -new -key server.key -out server.csr
```

This command will prompt you to enter information that will be incorporated into your certificate request. You'll need to provide the "Common Name", which is the domain name for which you are requesting the certificate.

Generate a self-signed certificate:

```bash
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
```

This command generates a self-signed certificate from the CSR that is valid for 365 days. The certificate is written to a file named server.crt.

Please note that these steps generate a self-signed certificate, which will not be trusted by clients by default. For a production server, you would typically use a certificate issued by a trusted Certificate Authority (CA).
