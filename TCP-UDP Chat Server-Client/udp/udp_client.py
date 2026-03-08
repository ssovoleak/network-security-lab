import socket 

# 1. Create the client socket 
client_udp=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. Send a mesage to the server 
host_ip= "127.0.0.1"
port = 12345

# 3. Send a message to the server and display the message received from the server
while True:
    message= input("Enter message: ")
    if message.lower() == "exit":
        break
    client_udp.sendto(message.encode(), (host_ip, port))
    response, addr= client_udp.recvfrom(1024)
    print("Server says:", response.decode())

# 4. Close the connection
client_udp.close()