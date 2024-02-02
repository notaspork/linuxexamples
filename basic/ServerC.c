#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

// Define data structures and global variables

typedef struct FileHeader {
    // Define structure members to hold file header information
    int numElements;
    int elementSize;
};

struct SerializedData {
    // Define structure members to hold serialized data
    char name[32];
    float price;
    short transactionType;
    long transactionTime;
};

char* gFilePath;
int gNetworkPort;
// Other configuration variables

// Function prototypes

void* handle_client(void* arg);
void read_data_from_file();
void write_data_to_file();
int initialize_server_socket();
void send_data(int client_socket, struct SerializedData* data);
void receive_data(int client_socket, struct SerializedData* data);
void parse_data(struct SerializedData* data);
void serialize_data(struct SerializedData* data);
void parse_command_line_arguments(int argc, char* argv[]);
void read_environment_variables();
void prompt_user_for_file();

// Function implementations

void* handle_client(void* arg) {
    // Handle client connection and data exchange
    // This is launched in its own thread
    int client_socket = *(int *)arg;
    // Handle client connection here
    // ...

    close(client_socket);
    return NULL;
}

void read_data_from_file() {
    // Read serialized data from file and store it in memory
}

void write_data_to_file() {
    // Write modifications to the file based on the data received from the client
}

int initialize_server_socket() {
    // Initialize the server socket and listen for incoming connections
    int server_socket;

    // Create a socket
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == -1) {
        perror("Failed to create socket");
        exit(1);
    }

    // Set up the server address
    struct sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(gNetworkPort);

    // Bind the socket to the server address
    if (bind(server_socket, (struct sockaddr*)&server_address, sizeof(server_address)) == -1) {
        perror("Failed to bind socket");
        exit(1);
    }

    // Listen for incoming connections
    if (listen(server_socket, 5) == -1) {
        perror("Failed to listen for connections");
        exit(1);
    }

    printf("Server socket initialized and listening on port %d\n", gNetworkPort);

    return(server_socket);
}

void send_data(int client_socket, struct SerializedData* data) {
    // Send data over the network to the client
}

void receive_data(int client_socket, struct SerializedData* data) {
    // Receive data from the client over the network
}

void parse_data(struct SerializedData* data) {
    // Parse the serialized data and extract integers and floating point numbers
}

void serialize_data(struct SerializedData* data) {
    // Serialize integers and floating point numbers into the desired format
}

void new_file(const char* filename) {
    // Function to handle new file
    printf("Creating new file: %s\n", filename);
}

#include <regex.h>

void parse_command_line_arguments_regex(int argc, char *argv[]) {
    regex_t regex;
    regmatch_t matches[3]; // We expect 2 matches: the whole string, the key, and the value

    // Compile the regular expression
    if (regcomp(&regex, "^--([^=]+)=(.+)$", REG_EXTENDED) != 0) {
        fprintf(stderr, "Failed to compile regex\n");
        exit(1);
    }

    for (int i = 1; i < argc; i++) {
        if (regexec(&regex, argv[i], 3, matches, 0) == 0) {
            // Copy the key and value into the Argument struct
            // strncpy(args[i-1].key, argv[i] + matches[1].rm_so, matches[1].rm_eo - matches[1].rm_so);
            // strncpy(args[i-1].value, argv[i] + matches[2].rm_so, matches[2].rm_eo - matches[2].rm_so);
        } else {
            fprintf(stderr, "Invalid argument: %s\n", argv[i]);
        }
    }

    // Free the compiled regular expression
    regfree(&regex);
}

void parse_command_line_arguments(int argc, char* argv[]) {
    // Parse command line arguments and set configuration settings, overriding environment variables if necessary
    int force_new = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-f") == 0 && i + 1 < argc) {
            char* gFilePath = argv[i + 1];
            i++; // Skip the next argument since it is the file path
        }
        else if (strcmp(argv[i], "-p") == 0 && i + 1 < argc) {
            gNetworkPort = atoi(argv[i + 1]);
            i++; // Skip the next argument since it is the port number
        }
        else if (strcmp(argv[i], "-n") == 0 && i + 1 < argc) {
            force_new = 1;
        }
    }
}

void read_environment_variables() {
    // Read environment variables
    char* filename = getenv("FILENAME");
    if (filename != NULL) {
        new_file(filename);
    }
}

int spinoff_new_thread(int client_socket) {
    pthread_t thread;
    if (pthread_create(&thread, NULL, handle_client, (void *)&client_socket) != 0) {
        perror("Failed to create thread");
        close(client_socket);
        return -1;
    }

    if (pthread_detach(thread) != 0) {
        perror("Failed to detach thread");
        close(client_socket);
        return -1;
    }

    // if no errors, return 0
    return 0;
}

void handle_new_connections(int server_socket) {
    struct sockaddr_in client_address;
    socklen_t client_len = sizeof(client_address);

    while (1) {
        int client_socket = accept(server_socket, (struct sockaddr *)&client_address, &client_len);
        if (client_socket == -1) {
            perror("Failed to accept client connection");
            continue;
        }

        handle_client(&client_socket);
        // if (spinoff_new_thread(client_socket) == 0)
        //     sleep(1);
    }
}

int main(int argc, char* argv[]) {
    int listen_socket;
    // Parse command line arguments and environment variables
    read_environment_variables();
    parse_command_line_arguments(argc, argv);

    // Read data from file
    read_data_from_file();

    // Initialize server socket
    listen_socket = initialize_server_socket();

    // Accept client connections and handle them in separate threads
    handle_new_connections(listen_socket);

    return 0;
}
