import socket 
import threading

# 1. Create client TCP socket 
client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ("Socket created successfully")

#define the server IP + port
host_ip = "127.0.0.1"
port = 22341

# 2. Connect to the server 
client.connect((host_ip, port))
print ("Connection successful")

def listen_for_messages(server_s):
    while True:
        try:
            data = server_s.recv(1024)
            if not data:
                break
            # Print the message and keep input prompt clean
            print (f"\rMessage from server: {data.decode()}")
        except:
            break

thread=threading.Thread(target= listen_for_messages, args=(client,), daemon=True)
thread.start()

while True: 
    message = input("Enter Message: ")
    # 3. Send a message 
    client.send(message.encode())
    if message.lower() == "exit":
        break

# 5. Close the connection 
client.close()
