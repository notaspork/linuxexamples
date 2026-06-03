# C Networking Introduction
Reference source file: `ServerC.c`

## Networking in C
For this lesson, we are going to write a networked server in C. We will start with the simple program we wrote in the last tutorial and build it up from there.

## Creating the server socket
Much like we did in Python, if we want to have a server, the server first needs to setup a socket to listen on. Let's start with defining `initialize_server_socket`:
```c
int initialize_server_socket() {

    int server_socket;
```
Since `initialize_server_socket` needs to return the listening server socket created and does not take any arguments, the function declaration begins with the `int` type to indicate the return type, but the argument list in the parentheses is empty since it has no arguments. This could also be written as `int initialize_server_socket(void)`. Both versions have the same result.

We also declare a `server_socket` _local variable_ of type `int` to store the created socket.

To implement this function, much like in the `ServerPython.py` version of `initialize_server_socket()` covered in the earlier Python tutorial module, we will call (the C versions of) the system `socket()` and `bind()` functions.

First, we need to call the system `socket()` function to create the new socket, then store the result in our `server_socket` _local variable_. Note that this is basically calling the same underlying system call as the Python version (more accurately, the Python `socket.socket()` function is calling this C version underneath the hood), where we call the constant `AF_INET` rather than Python's `socket.AF_INET` to specify an IPv4 socket, and the constant `SOCK_DGRAM` rather than Python's `socket.SOCK_DGRAM`, to specify a connectionless protocol (like UDP). If we instead wanted to specify a connection-oriented stream (like TCP), we would use `SOCK_STREAM`. The third argument to `socket()` specifies the protocol to be used with the socket. It is usually set to 0 to allow the system to automatically select the appropriate protocol based on the domain and type. This special value means that TCP would automatically be selected for a `AF_INET SOCK_STREAM` and UDP would automatically be selected for a `AF_INET SOCK_DGRAM` socket. It is also possible to explicitly specify a protocol with a protocol constant like `IPPROTO_TCP` that specifies the use of TCP regardless of what type of socket it is, which could result in very strange behavior on a `SOCK_DGRAM` socket and is not generally recommended.
```c
    // Create a socket
    server_socket = socket(AF_INET, SOCK_DGRAM, 0);
    if (server_socket == -1) {
        perror("Failed to create socket");
        exit(1);
    }
```
If the result of the `socket()` call is `-1` rather than a valid socket number (which would be non-negative), this means an error has occurred, so we will display an error message using the `perror()` standard C library function call and then kill the program with the `exit()` standard C library function call. In C, an `if` statement looks similar to a Python `if` statement, except that instead of using a colon and indentation to show the body of the `if` statement, the body (which gets executed if and only if the `if` condition is `true` or non-zero) is simply the statement that comes immediately after the `if` condition. This can either be a simple statement ending in a semicolon (i.e. `if (x>4) printf("x is greater than 4\n");`) or an entire clause in brackets (as shown in our `initialize_server_socket()` function above). Since C ignores whitespace, indentation and what line the condition and body are on do not matter like they do in Python `if` statements.

`perror()` formats and prints an error message passed as its argument to the `stderr` console, followed by a written error message based on the `errno` _global variable_, which is set by most standard library I/O functions. For example, if the `socket()` call fails due to insufficient permissions, errno might be set to `EACCES` (Permission denied), and the output of the above `perror()` call would be:
```
Failed to create socket: Permission denied
```
This is the same effect as calling `fprintf(stderr, "Failed to create socket: %s\n", strerror(errno));` where `strerror()` is another library function that returns a human readable description of the error number `errno`.

`exit()` performs cleanup tasks (e.g. flushing buffers, closing open file descriptors, etc) and then makes a system call (e.g. _exit() or exit_group() on Linux) to terminate the current process. The process exits with the argument provided being returned to whoever launched the process (such as another program or a Unix shell). A non-zero argument indicates an error condition, while a zero argument means no error occurred.

Much like Python provides many built-in libraries through the `import` command, C provides the C standard library (also known as `libc` or `glibc`) along with other C libraries like math and threads libraries. Since C is compiled, rather than interpreted like Python, external libraries often need to be included in two different ways.

First, in order for a program to compile without errors, we must use the `#include` _preprocessor directive_ to include the _header files_ with the right function or variable declarations, as mentioned in an earlier tutorial. In this case, we need to include the standard library _header files_ `stdio.h` for `perror()`, `stdlib.h` for `exit()`, and `sys/socket.h` for `socket()` as well as the constants `AF_INET` and `SOCK_DGRAM`. We will also shortly be using some additional data types and constants declared in `netinet/in.h`. If we wanted to access the `errno` _global variable_ provided by the standard library we would also need to `#include <errno.h>`, however our code does not use this variable directly. We already have `stdio.h`, but we will add the other three at the top of the file, so it now reads:
```c
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
```
Secondly, because an executable program works on compiled code, not source code, if we use any libraries in our program, we need to _link_ them to our compiled code in the final executable, or else there will be an undefined reference at run-time. We can do this by passing an additional `-l` flag to `gcc`:
```bash
gcc -o ServerC -lc ServerC.c
```
The `-lc` tells gcc to include the compiled `libc` library in the `ServerC` executable. Similarly, we could include the `libm` math library with `-lm` or the POSIX threads library `libpthread` with `-lpthread`. While many modern compilers like `gcc` will automatically include the standard C library `libc` in particular even without this flag, it should still be included for maximum portability. This is not necessary in Python because Python is (generally) an interpreted language where library source code is executed directly at run-time, whereas in C the compiled machine code of these libraries is needed to execute them, and they are compiled ahead of time, not at run-time.

One might ask, why doesn't C just compile libraries at run-time when needed? First, C is designed for high performance, and compiling libraries at run-time would introduce significant overhead, slowing down program execution. It also makes program execution more predictable, since the version of the compiler used is controlled by the developer at compile-time, as opposed to programs having to support a range of compilers if they were compiled at run-time. In some ways, C is essentially a highly-portable, easier-to-read version of assembly language, so it provides a high degree of control and visibility into what is actually happening on the raw hardware of a computer. This is sometimes critical when debugging certain problems, when high-performance or real-time performance is needed, or when working with very low-level code like device drivers or operating systems. Finally, while compiled machine code can be reverse-engineered, this is a lot more complex and difficult than reading and modifying source code, so some developers prefer to distribute only compiled code to make it more difficult to tamper with, copy, or work around. While C interpreters and Just-in-Time (JIT) compilers do exist, they are not commonly used for most mainstream programs for the above reasons. On the other hand, languages such as Java and others (including some implementations of Python) do use a JIT compiler to improve performance over a pure interpreter (but generally are still slower than purely compiled languages like C).

Getting back to setting up a listening socket, the next step in our `initialize_server_socket()` function is to call `bind()`, just as we did in `ServerPython.py`. In C, `bind()` takes exactly 3 arguments and returns an `int`. The return value is zero upon success and `-1` if an error occurred. Like most of the I/O functions in the standard C library, it will set the _global variable_ `errno` to indicate the specific error code, when it returns `-1`.

The first argument to `bind()` is the socket to bind to the server address (in this case `server_socket`), the second argument is the server address and port to bind the socket to, and the third argument tells `bind()` the size of the data passed through the second argument. This is necessary because the amount of data in an address can vary widely based on protocols. For example, an IPv4 address generally requires 32 bits but a full IPv6 address can use as many as 128 bits. To make this easier, the standard C library provides a data structure `sockaddr_in` for IPv4 addresses with a definition from the header file `netinet/in.h` that looks something like (this may vary slightly on different platforms):
```c
struct sockaddr_in {
    short sin_family;          // Address family (always AF_INET)
    unsigned short sin_port;   // Port number (in network byte order)
    struct in_addr sin_addr;   // IPv4 address
    char sin_zero[8];          // Padding to match `sockaddr` size
};
```
The `struct` keyword is used in C to indicate that a data type is a structure containing named fields, much like an object in Python (although it cannot contain functions). In the above type declaration, `sockaddr_in` is the name of the data type being defined. To setup a listening socket on the server's IPv4 address, we declare a new _local variable_ of type `sockaddr_in`, then assign values to its fields using the `.` operator:
```c
    struct sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(gNetworkPort);
```
`AF_INET` specifies the IPv4 address family, as before. Note that the `.sin_addr` field of a `sockaddr_in` is itself also a `struct`, so we set its `.s_addr` field to the constant `INADDR_ANY` which specifies that the socket should be bound to (and therefore be able to listen on) **ALL** available network interfaces on the host machine. It is equivalent to specifying the address `0.0.0.0`. If we only wanted the socket to be bound to a specific interface, we could instead specify the IP address of that particular interface. We set the `.sin_port` field to the port number we want to bind our listening socket to, in network byte order. We use the standard library function `htons` to convert the _global variable_ `gNetworkPort` which contains this port number, to network byte order, just like using the Python `.htons()` function from Python's `socket` module.

Once we have filled in the data in the `struct` `server_address`, we can pass it to `bind()`. As before, we check for an error condition (a `-1` return value of `bind()`) and print the appropriate error message if needed, before exiting. We use a special C operator called `sizeof()` that returns the size in number of bytes of whatever variable or data type in passed inside the parentheses of `sizeof()`. In this case, it tells `bind()` the number of bytes that `server_address` actually uses:
```c
    if (bind(server_socket, (struct sockaddr*)&server_address, sizeof(server_address)) == -1) {
        perror("Failed to bind socket");
        exit(1);
    }
```
The second argument to `bind()` utilizes two new concepts, typecasting and pointers.

## What is a pointer?
A pointer in C is a variable that stores the memory address of another variable. Instead of holding a value directly (like an integer or a character), a pointer holds the location in memory where that value is stored. Think of a pointer as a "reference" or a "map" to another variable. It tells you where to find the variable in memory. For example, consider the following code (which is not part of our example `ServerC.c` program):
```c
{
    int x = 42;
    int *ptr = &x;
}
```
In C, the `*` symbol is used to denote a pointer type. So while `x` is declared as an `int`, `ptr` is declared as an `int *` -- a memory address which points to an int, also known as an `int` _pointer_ data type. The `&` symbol is used to denote the address of the variable that comes after it (also known as a _reference_ to the variable), so the above code stores the address of `x` into the variable `ptr`, rather than the value of `x`.

In the example implementation, `int`s are 4 byte data types and big-endian (your platform may be different). If we were to use a debugger or other tool to view the memory of the process, we would see the data in memory as follows:
```
Address      Value          Description
--------------------------------------------
0x7ffe89b4   7f fe 89 b8    Value of `ptr` (address of `x`)
0x7ffe89b8   00 00 00 2a    Value of `x` (42 in decimal is 0x2a in hex)
```
In this example, the value of the variable `x` is stored at memory address 0x7ffe89b8 and the value of the variable `ptr` is stored at memory address 0x7ffe89b4, which contains the memory address of the variable `x` (also called a _reference_ to `x` or a _pointer_ to `x`).

Tying this back to the second argument of our `bind()` function call, we pass `&server_address`, which doesn't pass the actual value of the variable `server_address` to `bind()`, but rather passes it _by reference_, providing a `struct sockaddr_in` _pointer_ that contains the memory address of the `server_address` variable. This is necessary because the same `bind()` function handles binding many different types of sockets using many different protocols, not just network sockets using IPv4. As a result, some addresses (like an IPv6 address or Unix domain socket address) will have very different sizes and data structures compared to the `struct sockaddr_in` used for IPv4 addresses. That is why the third argument to `bind()` is needed to tell `bind()` exactly how large the data pointed to by the address passed into the second argument is.

## Type casting
To accomplish this in a strongly-typed language like C, there are separate address structures defined for each different address type. While we use `struct sockaddr_in` used for IPv4 addresses, `struct sockaddr_un` is used for Unix domain socket addresses (which are special non-network system sockets used for inter-process communication on Unix), and `struct sockaddr_storage` is a generic universal type large enough to store any socket address type. Since the function declaration for `bind()` requires an explicit type, but `bind()` needs to support all these different structures, `bind()` is actually declared using a generic abstract "shell" `struct sockaddr` which contains minimal fields and isn't large enough to store all socket address types. This is the C equivalent to an abstract base class that is never actually instantiated or used, but serves as a generic "stub" for a myriad of other types based on it.

However, since C is strongly-typed, for our code above the C compiler will generate an warning or error (depending on its exact settings) that we are attempting to pass a `struct sockaddr_in *` to a parameter of type `struct sockaddr *`. The compiler is warning us that the pointer type doesn't match, so we might be making a mistake. But in this case, we are intentionally passing a different pointer type by design, so we can override this warning/error by _casting_ the `struct sockaddr_in *` type to force the compiler to interpret it as a `struct sockaddr *` type. We do this by putting the desired type in parentheses before the variable we are _casting_, in this case `(struct sockaddr*)&server_address`. This forces the compile to treat our `&server_address` which is a `struct sockaddr_in *` type, as if it is a `struct sockaddr *` type, which is what `bind()` expects for its second argument. Since both of these pointer types are really just memory addresses, _casting_ one to the other doesn't actually change anything (they still both point to the same data, regardless of type), but it eliminates the compiler warning/error, which lets the compiler know that this wasn't a typo or accident, we intended to do it. This provides a powerful form a pointer polymorphism in C, much like object inheritance and base classes do in Python (and in C++).

Pointers are one of the more challenging parts of learning C for many people, so do not be discouraged if this is confusing, we will revisit it as we continue the tutorials.

Finally, we print a success message to the console using `printf()`, then return our newly bound `server_socket` to the calling function:
```c
    printf("Server socket initialized and listening on port %d\n", gNetworkPort);

    return(server_socket);
}
```

## Handling new incoming connections
Just as we did in `ServerPython.py`, we also need to define a new function `handle_new_connections()` to check to see if anyone has sent data to our new listening server socket, and if so, handle the client connections appropriately. Since `handle_new_connections()` doesn't return anything (or even return at all), we declare its return type as `void`. It takes a single argument, the listening server socket:
```c
void handle_new_connections(int server_socket) {
```
Why do we pass `server_socket` into our new function as a parameter, rather than just storing it in a _global variable_? Since a _global variable_ has global _scope_, it can be modified by any part of a program. Function parameters and _local variables_ are considered safer to use, since they have more restricted scopes and are therefore less likely to cause bugs because some other function used or modified a _global variable_ when we were not expecting it or that we forgot about. So the best practice is to prefer using function parameters and _local variables_ over _global variables_ when feasible. Can you think of another example of when we should've probably passed a function parameter instead of using a _global variable_?

Much as we did in Python, in the body of this function, we will loop forever. We use `while(1)` since any non-zero expression evaluates to true in C. The brace operators `{` and `}` contain the clause of code to be executed during each iteration of this infinite `while` loop.
```c
    while (1) {
        handle_client_udp(server_socket);
    }
}
```
Each interation, we call `handle_client_udp()` to read and respond to any data on the listening UDP socket. Therefore, we need to implement the `handle_client_udp()` function. This function will have a return type `void`, since it doesn't return anything, and will have one argument, the socket that is communicating with the client:
```c
void handle_client_udp(int client_socket) {
```
We need to declare a variable to store data received. We declare an array of type `char` for a generic memory buffer because `char` is the smallest common data type in C, usually a single byte on most platforms. The size of the array will determine how much memory is available in our buffer. Since we don't know exactly how much data to expect, we try to pick a size that will be large enough to at least avoid partial packets. Since our initial example will just echo back messages sent to it, we will pick 1024 bytes (1k) for our initial buffer size, which should be large enough for most short messages. To make it easy to change this later we will use the preprocessor's `#define` directive. At the top of the source code file, after the `#include` directives, we can add the following line of code:
```c
#define BUFFER_SIZE 1024
```
This uses the C preprocessor (which processes any line command that starts with a `#` character) to define a constant `BUFFER_SIZE` to resolve to 1024 anywhere in the source code. We will explore the C preprocesor more a little later in this lesson.

Now that this is defined, we can continue writing our `handle_client_udp()` function with the _local variable_ declarations:
```c
    char buffer[BUFFER_SIZE];
    struct sockaddr_in client_address;
    socklen_t client_len = sizeof(client_address);
```
We declare an IPv4 `struct sockaddr_in` to hold the client's address from the received UDP data, as well as a `socklen_t` which is a special type for socket sizes that holds the size of the `client_address` `struct` (which is the size in bytes of the `struct sockaddr_in` data type).

Now that the needed variables have been declared, we can call `recvfrom()` to get the next data chunk received on our server's UDP port. This is the C version of the Python `socket` module's `.recvfrom()` method. It returns the number of bytes of data received on the socket passed in as the first argument, or `-1` upon error (in which case `recvfrom()` will set the _global variable_ `errno` to the appropriate error code). If there is no data available, `recvfrom()` will block until data arrives (unless the socket was set to be non-blocking, in which case it immediately returns `-1` with `errno` set to `EAGAIN` or `EWOULDBLOCK`). This means that if `recvfrom()` (or the connection-oriented stream equivalent `recv()` used for TCP) ever returns `0`, it is not simply because there is no data, but indicates that the other side has finished transmitting all of their data and shut down their end of the connection. Since UDP is connectionless, this should never happen since there is no connection to shutdown, but it is important to note when using `recv()` for TCP. We store the result of `recvfrom()` in a _local variable_ `bytes_received`, then check to see it for errors (if `bytes_received` is negative), in which case we print an error message and `return` from this function.
```c
    int bytes_received = recvfrom(client_socket, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&client_address, &client_len);
    
    if (bytes_received < 0) {
        perror("Failed to receive data");
        return;
    }
```
The second argument to `recvfrom()` is a pointer to the address to store received data. While we declared `buffer` as a `char` array, in C this is still a type of _pointer_, since the array is simply a series of `char`s in memory, at the address pointed to by `buffer`. So passing `buffer` as the memory address for our buffer is the same as passing `&buffer[0]`, a _pointer_ to the first element in the `buffer` `char` array. The third argument is the size of this buffer. The fourth argument is an `int` that contains special flags for advanced usage (see the `man` page for details), and will always be `0` in our use cases of `recvfrom()`.

The fifth argument to `recvfrom()` is a _pointer_ to the structure where `recvfrom()` will store the address of the client that is sending the received data. The sixth argument is a _pointer_ to the length of the client's address data structure (in this case, the size of `struct sockaddr_in`). This sixth argument is used both by the caller to tell `recvfrom()` how much space is available to store the client's address data and then *also* used by `recvfrom()` to tell the caller how much of that space the returned client's address actually uses. While `recvfrom()` returns the number of bytes received as its return value, we need more information than just that. Passing a _pointer_ to the client address as the fifth argument allows `recvfrom()` to modify the data stored at the memory address of that _pointer_, which allows it to return more data than just the number of bytes received. Since as previously mentioned, there are different types of `struct sockaddr` data types that are different sizes, we also need to find out the size of this `client_address` data `struct`, which is why we need to pass a _pointer_ to the memory address of our `client_len` _local variable_, so that `recvfrom()` can store the correct size in `client_len`.

Why can't we just pass `client_address` and `client_len` to `recvfrom()`, rather than _pointers_? In C, all function arguments and return values are passed _by value_, meaning that a local copy is provided to or by the called function, so any modifications to those variables within that function will not affect the same variables outside of that function. In fact, best practice is generally to treat these arguments as _immutable_ to avoid confusion, although technically the copy can be modified and used by the function internally, the changes will just not be accessible outside the function. So, if `recvfrom()` were to assign `client_len = 32;` our calling `handle_client_udp()` function would still only see its version of `client_len` equal to `sizeof(client_address)` as we set it upon declaration, since changes to these function arguments are only local to the called function.

_Pointers_ allow us a way to pass variables _by reference_ instead of _by value_. A _pointer_ passed as an argument tells the called function the memory address of the data that the _pointer_ points to. While the called function cannot modify the _pointer_ argument itself and have those changes persist outside of the called function, the called function *can* go to the address referenced by the _pointer_ and modify the data there. Since this modifies the memory itself rather than just a local copy of an argument, these changes persist even outside of the called function. We will see more examples illustrating this in future lessons.

One more thing to note is that the sixth argument of `recvfrom()` is used for two different purposes. By telling `recvfrom()` the maximum data size of the client address `struct` available, `recvfrom()` can make sure it does not use more memory than is available. If it tried to write more data than this specified size, some of that data would end up overwriting other memory, which could contain other variables or possible even other code. This is known as a _buffer overflow_, and can result in undefined behavior, crashes, or security vulnerabilities that can be exploited. Instead, `recvfrom()` will truncate the client address data to fit in the specified size, which means the caller should always ensure this size is large enough to handle any possible address returned. If `recvfrom()` doesn't need all the memory available, it will modify the size pointed to by the sixth argument to indicate the amount of memory space it is actually using for the client's address.

Once we have the received data stored in the `buffer` array, we can print out the data, then send it back to the client who sent it, using the `printf()` and `sendto()` functions:
```c
    printf("Received message: %s\n", buffer);

    int bytes_sent = sendto(client_socket, buffer, bytes_received, 0,
                            (struct sockaddr *)&client_address, client_len);
}
```
As before, `sendto()` works much like its Python equivalent, but takes almost exactly the same arguments as `recvfrom()` above. We store the result, the number of bytes succesfully sent (although successfully sending them from the server doesn't guarantee that they were successfully *received* by the client), in a new `int` `bytes_sent`. Since the data we want to send in already in the `buffer` array and its length already in `bytes_received`, we can just pass these arguments directly. We can do the same for `client_address`, the destination we want to send the data back to, since it is the address of the client who sent us the data originally. The only difference is that `sendto()` expects us to pass the length of this client address `client_len` directly as the last argument, rather than a pointer to it, since it doesn't need to modify this length (since it is not changing `client_address`, it is simply the address to send the data to).

Wait, by that logic, then why are we still passing a _pointer_ to `client_address`, since like `client_len` the `client_address` is not modified by `sendto()`? `sendto()` expects a _pointer_ to `client_address` regardless, for two reasons. First, since there are several different types of addresses which all use different variants of `struct sockaddr`, a fixed type wouldn't work here, since `sendto()` supports multiple types (for example, both IPv4 and IPv6 addresses, which are different sizes). Unlike Python, C requires all variables and parameters to have explictly defined types at runtime, so it can efficiently allocate exactly the required amount of memory, and failing to do so will cause a compiler error. Second, because certain address types can be quite large, the overhead of trying to pass say, a 128-bit (16 bytes) address would cause a program to use more CPU cycles and memory than just passing a 64-bit (or 32-bit for 32-bit CPU architectures) _pointer_.

Finally, we need to modify our `main()` function to call `initialize_server_socket()` and `handle_new_connections()`, rather than `variable_test()`. First, we need to declare a _local variable_ `listen_socket` to store the new server socket returned from `initialize_server_socket()`. Then we need to pass this new server socket to `handle_new_connections()`:
```c
int main(int argc, char* argv[]) {
    int listen_socket;

    /*variable_test();*/

    // Initialize server socket
    listen_socket = initialize_server_socket();

    // Accept client connections and handle them in separate threads
    handle_new_connections(listen_socket);

    return 0;
}
```
We also added `/*` and `*/` _comment_ marks around the call to `variable_test()`. This is a C _comment_ block, and means that the compiler will ignore everything between these _comment_ marks, so `main()` will no longer call `variable_test()`. These traditional C _comment_ blocks can span multiple lines, so entire functions or source code files can be commented out easily using these symbols.

Beginning with C99, the version of the C standard published in 1999, C also supports the `//` _comment_ marks used in C++. These comments are line-specific and work like the `#` _comment_ mark in Python, so the compiler ignores everything from the `//` mark until the end of that line. We use these above to explain to the reader what the program is doing at each of the function calls in `main()`. Comments should be used frequently to explain the structure and function of code. While they do not replace the need for formal manuals or documentation or whole-function descriptions, getting in the habit of commenting while writing code makes it a lot easier to generate additional documentation later and makes the code much more readable, instead of having to remember or puzzle out exactly what is going on when looking back at a code segment later or when looking at someone else's code.

## Testing the C networking code
Now, we can test our new server. As before, we will be sure to include the standard C library with the `-l` option flag:
```bash
gcc -o ServerC -lc ServerC.c
./ServerC
```
Output:
```
Server socket initialized and listening on port -1
```
Port -1, that's not a valid UDP port! What is going on here? The `initialize_server_socket()` function uses the _global variable_ `gNetworkPort` to `bind()` the server socket to this port. But we never set theis port! Thankfully, this is easily recognized, since we initialized `gNetworkPort` to -1. While C initializes global variables to zero by default, local variables have no such guarantee, so it is best to initialize all variables that aren't going to be used immediately after their declaration, to avoid confusion. This prevents situations where you might have an undefined port number variable and spend hours trying to figure out why the server is listening on seemingly random ports.

But -1 isn't a valid port number, so why didn't `bind()` return an error when we gave it this port number? The answer is a nuance with the `htons()` function used to convert the endianess of our port number. `htons()` (on most modern platforms) expects an `unsigned short` value from 0-65535. However, -1 is a `signed` value, since it is a negative number. C implictly converts (also known as _implicit type casting_) this `signed` value to the data type that `htons()` expects, a 16-bit `unsigned` value. When the binary representation of -1 (0xFFFF in hex) is expressed as a 16-bit `unsigned` value, it is 65535 (which is also 0xFFFF in hex). Since 65535 is a valid port number, the `bind()` call will not return an error, unless the port is already in use or restricted. While the C compiler will often throw an error if you attempt to pass the wrong data type to a function they expects a different data type, if the data types are very close and the C compiler thinks it's "safe" (such as a smaller or less precise numerical type to a larger or more precise numerical type) the C compiler will _implictly cast_ the number or variable to the required type for you, when you normally would need to explictly _cast_ the type as we did when passing `(struct sockaddr*)&server_address` to `bind()` to force it to accept our `struct sockaddr_in *` instead of a `struct sockaddr *` type. Depending on the C compiler settings, _implict casting_ may result in an error or warning, but the default is generally to allow it, as a programmer convenience. That said, best practice is to never rely on _implict casting_ and always explictly _cast_ the type, to avoid confusion such as with port -1 being interpreted as port 65535. 

To fix this issue, let's `#define` another constant for the default port:
```c
#define SERVER_PORT 12345
```
We can the change the declaration of `gNetworkPort` to initialize it with this constant:
```c
int gNetworkPort = SERVER_PORT;
```
Now when we recompile, and then run our program we get:
```bash
gcc -o ServerC -lc ServerC.c
./ServerC
```
Output:
```
Server socket initialized and listening on port 12345
```
We can test our server by connecting to it using `nc` with the `-u` flag for UDP:
```bash
nc -u 127.0.0.1 12345
```
Let's type "Test" while running `nc`.

`nc` Output:
```
Test
Test
```
ServerC Output:
```
Received message: Test
```
Our simple UDP server correctly prints and echoes the message "Test" back to the `nc` client.

## TCP in C
Since our Python client is using TCP, and since we want a reliable, connection-oriented protocol for our server, let's modify the server to use TCP instead.

First, we need to modify `initialize_server_socket()` to setup a TCP socket instead of a UDP socket. To do this, we will change the second argument to the `socket()` function call near the top of the function to pass `SOCK_STREAM` instead of `SOCK_DGRAM`, so it reads:
```c
server_socket = socket(AF_INET, SOCK_STREAM, 0);
```
We will check for errors and `bind()` the `server_socket` regardless of whether we are using TCP or UDP, so that code stays the same. However, while UDP is _stateless_, TCP is a _connection-oriented_ protocol. This means that unlike UDP, which can send and receive data without maintaining explict connections, TCP needs to keep track of who it is connecting or connected to. Therefore with TCP, we need to set the `server_socket` up to listen for new incoming connections before it can process data received from them.

To do this, we call the standard C libary `listen()` function, which acts much like its Python equivalent (since the Python function is really just ultimately calling the C library's `listen()` anyway). `listen()` takes two arguments. The first argument is the socket to listen on, and the second argument is the size of the backlog of pending connections to use. Note that this backlog argument is not guaranteed to be honored on all platforms, but many operating system kernels will use it to size the maximum number of pending connections that the kernel will keep in its internal queue waiting for `accept()` calls, before refusing new incoming connection attempts. It returns `0` on success, `-1` on error and sets the _global variable_ `errno`, like most standard C library functions, so we check for this and print the appropriate error message for exiting on error:
```c
    if (listen(server_socket, 5) == -1) {
        perror("Failed to listen for connections");
        exit(1);
    }
```
The rest of `initialize_server_socket()` remains the same.

Next, we update `handle_new_connections()` to wait on a new connection and `accept()` it to get the newly connected socket, just as we did in Python. We first declare an IPv4 `struct sockaddr_in` to hold the connecting client's address, as well as a `socklen_t` which is a special type for socket sizes that holds the size of the `client_address` `struct`:
```c
void handle_new_connections(int server_socket) {
    struct sockaddr_in client_address;
    socklen_t client_len = sizeof(client_address);
```

Next, we add additional functionality to our `while (1)` infinite loop. Each interation, we define a variable `client_socket` which is local just to the `while` loop clause, and set it to result of calling `accept()`, which should be the newly connected socket. If it returns `-1`, then we print an error message and continue looping, otherwise we call `handle_client()` to handle the newly connected socket.
```c
    while (1) {
        int client_socket = accept(server_socket, (struct sockaddr *)&client_address, &client_len);
        if (client_socket == -1) {
            perror("Failed to accept client connection");
            continue;
        }

        handle_client(client_socket);
    }
}
```
`accept()` is like the Python socket `.accept()` method, except it takes 3 arguments. The first argument is the socket that the server is listening on, the second argument is a _pointer_ to the structure that the newly connected `client_address` data will be stored in by `accept()` and the third argument is a _pointer_ to the length of the client's address data structure. This third argument is used both by the caller to tell `accept()` how much space is available to store the client's address data and then *also* used by `accept()` to tell the caller how much of that space the returned client's address actually uses, much like with `bind()`.

We use the keyword `continue` upon error, rather than calling `exit()`, since an error while accepting a single connection should not be fatal and cause the entire server to shutdown, which would be disasterous for all the other clients the server should handle. When `continue` is used inside a `while` or `for` loop, it immediately skips to the next iteration of the loop, rather than executing the rest of the clause.

Also note that we need to pass this new `client_socket` to `handle_client()`, rather than `server_socket` as we were doing before, so that `handle_client()` is working with the connected socket, rather than with an unconnected listening server socket (which was alright for UDP, since UDP doesn't have connections anyway, but won't work for TCP).

Next, we need to implement the `handle_client()` function. This will look very similar to the `handle_client_udp()` function we already wrote, except we will need to replace the connectionless `recvfrom()` and `sendto()` function calls with TCP's connection-oriented `recv()` and `send()` function calls:
```c
void handle_client(int client_socket) {

    char buffer[BUFFER_SIZE];

    int bytes_received = recv(client_socket, buffer, BUFFER_SIZE, 0);
    if (bytes_received < 0) {
        perror("Failed to receive data");
        return;
    }

    printf("Received message: %s\n", buffer);
```
This time, instead of calling `recvfrom()`, we call `recv()`, which takes the same first four arguments as `recvfrom()` (the socket, a buffer to store the received data, the size of that buffer, and the special flags, which will be `0`), but doesn't require a fifth or sixth argument, since the `client_socket` already knows the address it is connected to, which is where the data will be received from. As a result, we also don't need to declare the `client_address` and `client_len` variables that we needed in `handle_client_udp()`. `recv()` also returns the same values as `recvfrom()`, the number of bytes read or `-1` on error.

Similarly, we next must replace the `sendto()` function call with `send()`, which also takes the same first four arguments as `sendto()` and returns the same values, but omits the fifth and sixth arguments, since it automatically sends the data to the socket's connected destination:
```c
    int bytes_sent = send(client_socket, buffer, bytes_received, 0);
    if (bytes_sent < 0) {
        perror("Failed to send response");
        return;
    }
```
Finally, since `client_socket` is actually connected somewhere, we must call the standard C library function `close()` to close this connection when we are finished. This informs the client on the other side of the connection that there is no more data and the session is over. `close()` takes a single argument, the socket with the connection to close.
```c
    close(client_socket);
}
```
If we do not close the connection, the client could be hanging and waiting a long time to receive additional data that will never come (although if the server eventually shuts down, the OS will automatically close all its sockets, but it's still best practice to explicitly close them as soon as we don't need them anymore).

## Testing the TCP networking code
Now we are ready to test the TCP version. Let's compile the program as before:
```bash
gcc -o ServerC -lc ServerC.c
```
Output:
```
ServerC.c:98:5: error: call to undeclared function 'close'; ISO C99 and later do not support implicit function
      declarations [-Wimplicit-function-declaration]
   98 |     close(client_socket);
      |     ^
1 error generated.
```
What happened? The compiler could not find a declaration for the `close()` function. Why not, if we included all the socket functions in `sys/socket.h`?

The difference is that the POSIX `close()` function call is designed to work on sockets, but also on a wider range of POSIX constructs, such as files and pipes, so POSIX puts its prototype in `unistd.h`, along with basic system calls like `read()` and `write()`, which are similarly broad. In contrast, function calls like `socket()`, `bind()`, and `recv()` only work on sockets, not on file descriptors or pipes, so they are all in `sys/socket.h`.

Therefore we need to add an additional `#include` line to use this header file at the top of our source code:
```c
#include <unistd.h>
```

Now when we recompile, and then run our program we get:
```bash
gcc -o ServerC -lc ServerC.c
./ServerC
```
Output:
```
Server socket initialized and listening on port 12345
```
We can test our server by connecting to it using `nc` (without the `-u` flag this time):
```bash
nc 127.0.0.1 12345
```
Let's type "Test" while running `nc`.

`nc` Output:
```
Test
Test
```
ServerC Output:
```
Received message: Test
```
Our simple TCP server now correctly prints and echoes the message "Test" back to the `nc` client.
