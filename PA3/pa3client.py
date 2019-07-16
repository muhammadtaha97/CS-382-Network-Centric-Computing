import socket
import sys
import hashlib
import threading
import time
import os


maxnumbernodes = 10
global nodes
nodes = []

def addtoDHT(thisnode, anotherport):
	client_sock = socket.socket()
	client_sock.connect((thisnode.ip,anotherport))
	client_sock.send("Please Add Me to the DHT".encode())
	responsefromserver = client_sock.recv(1024).decode()

	if responsefromserver == "Yes, Sure":
		#print("Halo")
		client_sock.send(str(thisnode.port).encode())
		messagefromserver = str(client_sock.recv(1024).decode())
		if messagefromserver == "There are now just the two of us":
			print(messagefromserver)
			thisnode.successor = anotherport
			thisnode.predecessor = anotherport
		elif messagefromserver == "Yeah, good to have more than two":
			print(messagefromserver)
			client_sock.send("Please send me port of your successor")



def checksinglenode(thisnode):
	if thisnode.successor == thisnode.port and thisnode.predecessor == thisnode.port:
		return True
	else:
		return False

def leaving(thisnode):
	if checksinglenode(thisnode) == True:
		print("Bye. I am leaving")
		os._exit(0)
	print("Bye. I am leaving")
	successor_socket = socket.socket()
	successor_socket.connect((thisnode.ip,thisnode.successor))
	successor_socket.send(str("Bye. I am leaving.").encode())
	message = str(successor_socket.recv(1024).decode())
	successor_socket.send(str(thisnode.port).encode())
	successor_socket.close()
	
	predecessor_socket = socket.socket()
	predecessor_socket.connect((thisnode.ip,thisnode.predecessor))
	predecessor_socket.send(str("Bye. I am leaving.").encode())
	message = str(predecessor_socket.recv(1024).decode())
	predecessor_socket.send(str(thisnode.port).encode())
	predecessor_socket.close()
	os._exit(0)




def gethashport(ip,port):
	thishash = hashlib.sha1(ip.encode() + port.encode())
	thishash = thishash.hexdigest()
	return thishash

def gethashfilename(filename):
	thishash = hashlib.sha1(filename.encode())
	thishash = thishash.hashdigest()
	return thishash

class Node:
	def __init__(self, ip, port):
		self.port = port
		self.ip = ip
		self.successor = port
		self.predecessor = port
		self.hash = gethashport(str(host), str(port))
		self.fingertable = ["" for i in range (0,5)]
		self.files = []

def nodeinfo(thisnode):
	print("My Port is: ", thisnode.port)
	print("My Successor is: ", thisnode.successor)
	print("My Predecessor is: ", thisnode.predecessor)
	print("My Hash is: ", thisnode.hash)
	print("My files are: ", thisnode.files)

def menu():
	print("Press 1 to Print Node Info (Predecessor, Successor and the Port number etc. for this node): ")
	print("Press 2 to print fingertable of Node: ")	
	print("Press 3 to store file: ")
	print("Press 4 to download file: ")
	print("Press 5 to leave: ")


def sthread(thisnode, anotherclient):
	responsefromclient = str(anotherclient.recv(1024).decode())
	if responsefromclient == "Please Add Me to the DHT":
		anotherclient.send("Yes, Sure".encode())
		receiveport = int(anotherclient.recv(1024).decode())
		print("Connection Initiated with Node with port number: ", receiveport)
		if (checksinglenode(thisnode) == True):
			thisnode.predecessor = receiveport
			thisnode.successor = receiveport
			anotherclient.send("There are now just the two of us".encode())
		else:
			anotherclient.send("Yeah, good to see more than two".encode())
	elif responsefromclient == "Bye. I am leaving.":
		anotherclient.send("Okay, you can leave".encode())
		receiveleavingport = int(anotherclient.recv(1024).decode())
		print("Node with port number ",receiveleavingport, " has left")
def cthread(thisnode):
	while True:
		menu()
		choice = int(input())
		if choice == 1:
			nodeinfo(thisnode)
		elif choice == 2:
			printfingertable(thisnode)
		elif choice == 3:
			storefile(thisnode)
		elif choice == 4:
			downloadfile(thisnode)
		elif choice == 5:
			leaving(thisnode)
		else:
			continue




if __name__ == "__main__":
	# host = int(sys.argv[1])
	# port = int(sys.argv[2])
	host = '127.0.0.1'
	#port = int(input("Please enter your port: "))
	port = 1
	thisnode = Node(host,port)
	#print(firstnode.hash)
	# print(firstnode.successor)
	mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	mysocket.bind((host,port))
	mysocket.listen(100) 

	while True:
		print("Press 1 if you have port number of another node: ")
		print("Press 2 if you do not have other port number: ")
		#choice = int(input())
		choice = 1
		if (choice == 1):
			#anotherport = int(input("Please enter the port number of the other node: "))
			anotherport = 2
			addtoDHT(thisnode, anotherport)
			clientThread = threading.Thread(target=cthread, args=(thisnode,))
			clientThread.start()
			while True:
				anotherclient, address = mysocket.accept()
				print(anotherclient)
				serverThread = threading.Thread(target = sthread, args = (thisnode,anotherclient))
				serverThread.start()
		elif(choice == 2):
			clientThread = threading.Thread(target=cthread, args=(thisnode,))
			clientThread.start()			
			while True:
				anotherclient, address =mysocket.accept()
				serverThread = threading.Thread(target = sthread, args = (thisnode,anotherclient))
				serverThread.start()
		else:
			continue


	
