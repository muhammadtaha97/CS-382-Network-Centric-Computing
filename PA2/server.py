import socket
from _thread import *
import threading



serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(('localhost', 8080))
serv.listen(2)
print("Waiting for a connection")

def threaded_client(client):
    print ("Accepted connection from: ", client)
    msg = "Welcome to the server"
    client.send(msg.encode())
            
    # with clients_lock:
    # clients.add(client)
    while True:
        data = client.recv(1024)
        if not data: 
            # count = count - 1 
            break
        from_client = data.decode("utf-8")
        # print(from_client)
        # msg = str(from_client)
        # with clients_lock:
        # if count == 1:
        #     win = "YOU WON"
        #     client.send(win.encode())
        for c in connection:
            c.sendall(data)
    # with clients_lock:
    #     clients.remove(client)
    #     client.close()  
    #     print('client disconnected')    
    # count = count + 1
    # if count == 2:
    
    client.close()
    print('client disconnected')

count = 2
counter = 0 
connection = []
# clients = set()
msg = "Welcome to the server"
# clients_lock = threading.Lock()
while True:
    conn, addr = serv.accept()
    connection.append(conn)
    counter = counter + 1
    if counter == 2:
        for i in range(2):
            start_new_thread(threaded_client, (connection[i],))









   