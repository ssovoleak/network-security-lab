import socket
import threading
import logging 


#Setup logging
logging.basicConfig(
   filename="server.log",  #the file to save logs to
   level= logging.INFO,  #only record INFO level messages and above
   format="%(asctime)s | %(message)s",  #how each log line look
   datefmt= "%Y-%m-%d %H:%M:%S" #how the timestamp looks
)

def log(message):
   print(message) #shows it live in the terminal 
   logging.info(message) #saves it permanently to server.log

# 1. Create the server class
server= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("Socket successfully created!")
#Define IP Add + port
host_ip = "0.0.0.0"
port = 22341
# 2. Bind the IP + port 
server.bind((host_ip, port))
print("Socket binded to %s" %(port))

# 3. Put the socket into listening mode
server.listen()
log(f"Server started | Listening on port {port}")

# Store all connected clients
clients=[]

# Broadcast message to all clients except the sender 
def broadcast(message, sender_address, sender_socket):
   for client in clients:
      if client != sender_socket:
        try:
            client.send(f"{sender_address} says {message}".encode())
        except:
           #Remove client if sending fails 
           clients.remove(client)
        
# 4. create a fucntion to handle client connection
def handle_client(client_s, client_address):
    log(f"New Connection | IP: {client_address[0]} | Ephemeral Port: {client_address[1]}")
    while True:
       # 5. receiving the message from client
       data= client_s.recv(1024)
       # 6. if the client is not connected
       if not data:
        log(f"DISCONNECTED | IP: {client_address[0]} | Ephemeral Port: {client_address[1]}")
        break
       
       # 7. decode the data from client into human readable form
       message= data.decode()
       log(f"MESSAGE | IP:{client_address[0]} | Ephemeral Port: {client_address[1]} | Message: {message}")

       # 8. Broadcast to all other clients 
       broadcast(message, client_address, client_s)
       client_s.send("message received".encode())

       # 9. handle exit request from the client to disconnect and close the connection
       if message.lower() == "exit":
        log(f"EXIT REQUEST | IP: {client_address[0]} | Ephemeral Port: {client_address[1]}")
        break
    clients.remove(client_s)
    client_s.close()

# 10. Main server loop, always accept new clients, create a new thread for each client that will be runniing handle_client
while True:
    client_s, client_address = server.accept()
    clients.append(client_s)
    thread= threading.Thread(target=handle_client, args=(client_s, client_address))
    thread.start()
