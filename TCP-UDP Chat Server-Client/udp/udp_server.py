import socket

# 1. Create the UDP server 
server_udp= socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
# 2. Bind IP + Port 
host_ip= "127.0.0.1"
port = 12345

server_udp.bind((host_ip, port))
print(f"UDP is listening on {host_ip}:{port}")

while True:
    # 3. Receive the message from the client 
    data, addr= server_udp.recvfrom(1024)
    message = data.decode()
    print("Received message:", message, "from", addr)

    # 4. Send a response back to the client (optional)
    server_udp.sendto("Message received".encode(), addr)

    if message.lower() == "exit":
        print("Client requested exit")
        break

server_udp.close()
