# TCP Chat Server & Client

A multi-client TCP chat server built from using Python's socket and threading modules. Supports simultaneous conenctions, message broadcasting, connection logging, and smooth disconnection.

## How It Works

The server binds to a port and listens for incoming connections. Each connected client gets its own dedicated thread so multiple clients can send and receive message simultaneously. When a client sends a message, the server broadcasts it to all other connected clients. All activity is logged to a file with timestamps.

## Features

- Multi-client support using threading
- Message broadcasting to all connected clients
- Automatic detection of disconnected clients
- Full logging of connections, messages, and disconnections
- Tested across multiple devices.

## Files

- tcp_server.py: TCP server with threading, broadcasting, and logging
- tcp_client.py: TCP client with separate listening thread
- screenshots/: Terminal output and Wireshark captures

## Configuration

In tcp_server.py:
host_ip = "0.0.0.0" # listen on all interfaces
port = 22341 # change to any available port

In tcp_client.py:
host_ip = "127.0.0.1" # local machine
host_ip = "192.168.x.x" # another device on the same network

## How to Run

Start the server:
python3 tcp_server.py

Connect a client (open a new terminal)
python3 tcp_client.py

Connect multiple clients by opening more terminals and running tcp_client.py in each one. Messages sent from one client will appear on all others.

Type "exit" to disconnect a client properly.

## Key Concepts Demonstrated

TCP 3-way handshake:

- Each client connection starts with SYN -> SYN-ACK -> ACK
- Handled automatically by the OS before accept() returns

Ephemeral ports:

- Each client connection gets a unique temporary port assigned by the OS
- Visible in the server log an in Wireshark captures

Threading:

- Without threads, the server can only handle one client at a time
- Each client gets its own thread so recv() blocking doesn't affect others
- What happens here is concurrency (rapid switching) not true parallelism

Logging:

- All events saved to server.log with timestamps
- Record new connections, messages, exit requests, disconnections

## Wireshark Observations

Captured on bridge100 (UTM virtual network) with filter tcp.port == 22341

Flags observed:

- SYN, SYN-ACK, ACK -> 3-way handshake on connection
- PSH, ACK -> actual message data (only packets with PSH contain messages). Push flag in TCP packet ensures low-latency delivery, containing data that needs to be pushed to the application layer immediately.
- FIN, ACK -> 4 way termination on disconnection

Messages appeared in plain text in Wireshark confirming that encoding (encode/decode) provides no security - it is purely a transmission format requirement.
