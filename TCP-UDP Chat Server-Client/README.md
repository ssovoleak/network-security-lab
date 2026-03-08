# Socket Programming - TCP & UDP Chat implementation

A hands-on networking project built to understand how data moves across a network at the socket level. This project covers both TCP and UDP communication protocols, implemented in Python without any networking frameworks.

## Project Structure

- TCP/- Multi-client TCP chat server with threading, broadcasting, and logging.
- UDP/- UDP message exchange demonstrating connectionless communication
- notes/- Personal study notes covering all concepts learned.

## What I Learned

- How TCP and UDP differ at the implementation level
- How the 3-way handshake works in practice
- How ephemeral ports are assigned per session
- How threading enables multiple simultaneous client connections
- How to capture and analyze live network traffic using Wireshark
- Why encoding is not encryption and why that matters in security
- How to set up and use Linux VM for networking testing

## Design Approach

This project replicates a basic chatroom scenario where every message sent by one client is broadcasted to all other connected clients, similar to a group chat. This is to demonstrate how servers acts as a message router between multiple TCP connections.

Each client gets its own dedicated thread so the server can handle multiple simultaneous connections without blocking. The server sits in the middle of all communication. Clients never talk directly to each other, all messages are routed through the server.

## Limitation and Future Improvements

- Broadcasting sends messages to all connected clients (group chat model): in a real application, private messaging would require additional logic to route messages to a specific client only.

- No encryption: messages are transmitted in plain text and are fully visible when analyzed via Wireshark. Real application would utilise TLS/SSL to secure data in transit.

- No authentication: any cient can connect without credentials. A real system would require login, sessions, and access control.

## Technologies Used

- Python (socket, threading, logging modules)
- Ubuntu Server (VM via UTM on macOS)
- Wireshark (packet capture and traffic analysis)
- macOS Terminal + SSH

## How to Run

Clon the repository:
[URl]

Run TCP server:
cd tcp
python3 tcp_server.py

Run TCP client (separate terminal):
cd tcp
python3 tcp_client.py

Run UDP server:
cd udp
python3 udp_server.py

Run UDP client:
cd udp
python3 udp_client.py
