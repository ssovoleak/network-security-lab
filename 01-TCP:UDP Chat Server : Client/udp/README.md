# UDP Server & Client

A UDP message exchange implementation built using Python's socket module. Demonstrates how connectionless communication works and how it differs from TCP.

## How It Works

Unlike TCP, UDP doesn't establish a connection before sending data. The server binds to a port and waits for incoming datagrams. The client sends messages directly without a handshake. There is no guarantee that the message will arrive or arrive in order. The server runs continuously until the client send "exit".

## Files

- udp_server.py: UDP server that receives messages and responds
- udp_client.py: UDP client that sends messages to the server

## How to Run

Start the server:
python3 udp_server.py

Run the client (new terminal):
python3 udp_client.py

Type a message and press Enter to send.
Type "exit" to disconnect and shut down the server.

# Key Differences from TCP

- Does not required 3-way handshake, connectionless
- No guaranteed delivery
- Data does not arrive in order
- Faster
- Mostly used for streaming, gaming, DNS, DHCP...

## Key Concepts Demonstrated

No handshake:

- Client sends immediately without establishing a connection
- No SYN, SYN-ACK, ACK sequence
- Faster but no confirmation data was received

sendto()

- TCP uses send() becasue the connectio is already established
- UDP uses sendto() because there is no connection, the destination must be specified with every single message

recvfrom()

- TCP uses recv() because the connection tracks who sent the data
- UDP uses recvfrom() because there is no connection, it returns both the data and the sender's address so the server knows who to respond to.

No threading required:

- Each datagram is independent
- There is no persistent connection to manage
- No need to handle multiple simulateous connections

No client bind:

- The OS automatically assigns an ephemeral port when sendto() is called

## Limitation

- Single client only
- No encryption: messages are transmitted in plain text
- No delivery confirmation: if a message is lost, neither side would be aware
- Server only shuts down when client sends "exit": there is no server-side exit handling.
