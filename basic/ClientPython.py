import socket
import ssl
import DataStructuresPython as ds
import struct
import os
import re
QUERY_LOG_PATH = 'query_log.txt'
filterStack = ds.Stack()
FILTER_PATTERN = re.compile(r'([a-zA-Z ]+)([=<>!]+)([^,]+)')

SERVER_NAME = 'localhost'
SERVER_PORT = 12345

def is_valid_ip(ip):
    # Check if it's a valid IPv4 address
    parts = ip.split('.')
    if len(parts) == 4:
        for part in parts:
            if not part.isdecimal() or not 0 <= int(part) <= 255:
                return False
        return True
    
    # Check if it's a valid IPv6 address
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        return True
    except socket.error:
        return False

def load_file_data(file_path):
    logs = ds.PriorityQueue()
    with open(file_path, 'r') as file:
        for line in file:
            try:
                parsedLine = line.split(',')
                if len(parsedLine) != 8:
                    raise Exception("Wrong number of elements in log entry")

                logEntry = {'username': parsedLine[0].strip(),
                    'IP': parsedLine[1].strip(),
                    'port': int(parsedLine[2].strip()),
                    'accessTime': int(parsedLine[3].strip()),
                    'dataSent' : int(parsedLine[4].strip()),
                    'dataReceived' : int(parsedLine[5].strip()),
                    'score' : float(parsedLine[6].strip()),
                    'server': parsedLine[7].strip()}

                if not is_valid_ip(logEntry['IP']):
                    print('Invalid IP: {}'.format(logEntry['IP']))
                    raise Exception('Invalid IP: {}'.format(logEntry['IP']))
                
                logs.enqueue(logEntry, logEntry['accessTime'])
                # print("Added logEntry: {}".format(logEntry))
            except:
                print('Invalid log line: {}'.format(line))
    return logs

def save_last_query_action(query):

    # Check if the log file exists. If not, create it
    if not os.path.exists(QUERY_LOG_PATH):
        open(QUERY_LOG_PATH, 'w').close()

    with open(QUERY_LOG_PATH, 'r+') as file:
        first_line = file.readline()[len('Total filters: '):].strip()
        try:
            num_queries = int(first_line)
        except ValueError:
            num_queries = 0
        finally:
            num_queries += 1
        
        file.seek(0)
        file.write(f'Total filters: {num_queries:<16}\n')
        file.seek(0, os.SEEK_END)
        file.write(query + '\n')
        file.flush()

        # Print the new size of the file to console
        print(f"Updated query log. New size = {os.path.getsize(QUERY_LOG_PATH)} bytes")

def remove_last_query_action():
    with open(QUERY_LOG_PATH, 'r+') as file:
        lines = file.readlines()
        first_line = lines[0][len('Total filters: '):].strip()
        try:
            num_queries = int(first_line)
        except ValueError:
            num_queries = 0

        if num_queries < 1:
            raise ValueError("No queries to remove")

        num_queries -= 1
        file.seek(0)
        file.write(f'Total filters: {num_queries:<16}\n')
        file.writelines(lines[1:-1])  # Write all lines except the last one
        file.truncate()
        print(f"Updated query log. New size = {file.tell()} bytes")

class SERVER_COMMANDS:
    UPLOAD_CMD = 0x0001
    QUERY_CMD = 0x0002

def send_log_entry(sock, logEntry):
    # Pack the username, IP, and server as separate fields
    username = logEntry['username'].encode('utf-8')
    ip = logEntry['IP'].encode('utf-8')
    server = logEntry['server'].encode('utf-8')

    # Create a format string for the struct
    fmt = '!HHH{}s{}s{}sHIIIf'.format(len(username), len(ip), len(server))

    # Pack all the data into a single binary structure
    packed_data = struct.pack(fmt,
                                len(username), len(ip), len(server),
                                username, ip, server,
                                logEntry['port'],
                                logEntry['accessTime'],
                                logEntry['dataSent'],
                                logEntry['dataReceived'],
                                logEntry['score'])

    # Send the packed data
    sock.sendall(packed_data)

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('Socket connection broken')
        data += more
    return data

def recv_log_entry(sock):
    # Receive the length of the username, IP, and server fields
    lengths_fmt = '!HHH'

    lengths_data = recv_all(sock, struct.calcsize(lengths_fmt))
    username_len, ip_len, server_len = struct.unpack(lengths_fmt, lengths_data)

    # Create a format string for the struct with the received lengths
    fmt = f'!{username_len}s{ip_len}s{server_len}sHIIIf'

    # Unpack the data from the socket
    data = recv_all(sock, struct.calcsize(fmt))
    unpacked_data = struct.unpack(fmt, data)

    # Extract the fields from the unpacked data
    username = unpacked_data[0].decode('utf-8')
    ip = unpacked_data[1].decode('utf-8')
    server = unpacked_data[2].decode('utf-8')

    # Create a dictionary with the extracted fields
    logEntry = {
        'username': username,
        'IP': ip,
        'port': unpacked_data[3],
        'accessTime': unpacked_data[4],
        'dataSent': unpacked_data[5],
        'dataReceived': unpacked_data[6],
        'score': unpacked_data[7],
        'server': server
    }

    return logEntry

def upload_logs(sock, logs):
    # send a 2-byte integer with the command
    sock.sendall(sock.htons(SERVER_COMMANDS.UPLOAD_CMD))
    # send a 4-byte integer with the number of log entries
    upLen = sock.htonl(len(logs))   # htonl is a function that converts a 32-bit integer from host byte order to network byte order
    sock.sendall(upLen)
    while len(logs) > 0:
        logEntry = logs.dequeue()
        print('Uploading log entry: {}'.format(logEntry))
        # send log entry to server
        send_log_entry(sock, logEntry)

def apply_filter(results, filter_query):
    matches = FILTER_PATTERN.findall(filter_query)
    filtered_results = []
    for item in results:
        matchCount = len(matches)
        for field, operator, value in matches:
            matchCount -= 1
            field = field.strip()
            value = value.strip()
            if not field in item:
                raise ValueError("Field not found: {}".format(field))
            entry_value = item[field]

            if isinstance(entry_value, str):
                if operator == '=' and entry_value != value:
                    break
                elif operator == '!=' and entry_value == value:
                    break
            elif isinstance(entry_value, int) or isinstance(entry_value, float):
                if operator == '=' and entry_value != float(value):
                    break
                elif operator == '!=' and entry_value == float(value):
                    break
                elif operator == '<' and entry_value >= float(value):
                    break
                elif operator == '>' and entry_value <= float(value):
                    break
                elif operator == '<=' and entry_value > float(value):
                    break
                elif operator == '>=' and entry_value < float(value):
                    break
            else:
                raise ValueError("Invalid value type: {}".format(type(entry_value)))
            
            if matchCount == 0:
                filtered_results.append(item)

    return filtered_results

def get_filter_string():
    print("Enter filter query as a string with fields separated by commas (i.e. username=Alice, score>4, score<9.5)")
    print("Valid fields: username (client's username), IP (client IP), server (server name/IP), port (server port), accessTime (as an integer), dataSent (bytes sent by client), dataReceived (bytes sent to client), score (floating point)")
    print("Valid operators: =, <, >, <=, >=, !=")
    filter = input('Enter filter: ')
    return filter
 
def submit_query(sock, query):
    sock.sendall(sock.htons(SERVER_COMMANDS.QUERY_CMD))
    queryData = query.encode('utf-8')
    sock.sendall(sock.htonl(len(queryData)))
    sock.sendall(queryData)

    # receive query results from server
    num_results = recv_all(sock, 4)
    num_results = sock.ntohl(num_results)
    results = []
    for i in range(num_results):
        logEntry = recv_log_entry(sock)
        results.append(logEntry)
    return results

def do_menu(sock):
    curFilterString = ''
    curResults = []
    if os.path.exists(QUERY_LOG_PATH):
        os.remove(QUERY_LOG_PATH)
    
    while True:
        try:
            print('Connected to server {}:{}'.format(SERVER_NAME, SERVER_PORT))
            print('Last filter: {} matching {} results'.format(curFilterString,len(curResults)))
            print('Please choose an option:')
            print('1. Upload log file to server')
            print('2. Submit new query to server')
            print('3. Filter query results')
            print('4. Undo last query/filter')
            print('5. Display current query results')
            print('6. Clear all query results')
            print('7. Exit')
            choice = input('Enter choice: ')
            if choice.startswith('1'):
                file_path = input('Enter the path to the log file to upload: ')
                logs = load_file_data(file_path)
                print('Loaded {} log entries successfully'.format(len(logs)))
                if (len(logs) > 0):
                    # send logs to server
                    upload_logs(sock, logs)
            elif choice.startswith('2'):
                curFilterString = get_filter_string()
                curResults = submit_query(sock, curFilterString)
                filterStack.push((curResults, curFilterString))
                save_last_query_action(curFilterString)
            elif choice.startswith('3'):
                curFilterString = get_filter_string()
                curResults = apply_filter(curResults, curFilterString)
                filterStack.push((curResults, curFilterString))
                save_last_query_action(curFilterString)
            elif choice.startswith('4'):
                # undo last filter
                if len(filterStack) > 0:
                    filterStack.pop()
                    remove_last_query_action()
                    if len(filterStack) > 0:
                        curResults, curFilterString = filterStack.pop()
                        filterStack.push((curResults, curFilterString))
                    else:
                        curResults = []
                        curFilterString = ''
                else:
                    print('No filters to undo')
            elif choice.startswith('5'):
                # display results
                print('Current query results:')
                print(curResults)
            elif choice.startswith('6'):
                # delete log file
                os.remove(QUERY_LOG_PATH)
                filterStack.clear()
            elif choice.startswith('7'):
                return
            else:
                print('Invalid choice. Please try again.')
        except Exception as e:
            print('Error: {}'.format(e))

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

def start_client_simple_ssl():
    with socket.create_connection((SERVER_NAME, SERVER_PORT)) as sock:
        with create_ssl_socket(sock) as ssock:
            send_data_simple(ssock)
            receive_data_simple(ssock)

def start_client():
    with socket.create_connection((SERVER_NAME, SERVER_PORT)) as sock:
        do_menu(sock)

print('Starting client...')
start_client()
