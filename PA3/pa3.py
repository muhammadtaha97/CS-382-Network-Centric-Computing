import socket
import sys
import hashlib
import threading
import time
import os


maxnumbernodes = 10

global ip
ip = '127.0.0.1'


def gethashport(ip,port):
	thishash = hashlib.sha1(ip.encode() + port.encode())
	thishash = thishash.hexdigest()
	return thishash

def gethashfilename(filename):
	thishash = hashlib.sha1(filename.encode())
	thishash = thishash.hexdigest()
	return thishash

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
			client_sock.send("Please send me port of your predecessor".encode())
			predecessorport = int(client_sock.recv(1024).decode())
			predecessorporthash = gethashport(ip,predecessorport)
			anotherporthash = gethashport(ip,anotherport)
			if predecessorporthash > anotherporthash and thisnode.hash > anotherporthash and thisnode.hash > predecessorporthash:
				thisnode.predecessor = predecessorport
				thisnode.successor = anotherport
				client_sock.send(str("Could easily adjust between the predecessor and the port.").encode())
			elif predecessorporthash < anotherporthash and thisnode.hash < anotherporthash and thisnode.hash > predecessorporthash: 
				thisnode.predecessor = predecessorport
				thisnode.successor = anotherport
				client_sock.send(str("Could easily adjust between the predecessor and the port.").encode())				
			elif predecessorporthash > anotherporthash and thisnode.hash < anotherporthash and thisnode.hash < predecessorporthash:
				thisnode.predecessor = predecessorport
				thisnode.successor = anotherport
				client_sock.send(str("Could easily adjust between the predecessor and the port.").encode())
			else:
				client_sock.send(str("Could not easily adjust between the predecessor and the port. Need Successor port Now").encode())
				successorport = int(client_sock.recv(1024).decode())
				addtoDHT(thisnode, successorport)


	client_sock.close()



def checksinglenode(thisnode):
	if thisnode.successor == thisnode.port and thisnode.predecessor == thisnode.port:
		return True
	else:
		return False

def leaving(thisnode):
	print("Bye. I am leaving")
	if checksinglenode(thisnode) == True:
		os._exit(0)
	successor_socket = socket.socket()
	successor_socket.connect((thisnode.ip,thisnode.successor))
	successor_socket.send(str("Bye. I am your predecessor and I am leaving.").encode())
	message = str(successor_socket.recv(1024).decode())
	successor_socket.send(str(thisnode.port).encode()) #Okay tell me your port
	finalresponse = str(successor_socket.recv(1024).decode())
	print(finalresponse)
	if finalresponse == "Please send me your predecessor before leaving":
		successor_socket.send(str(thisnode.predecessor).encode())
	successor_socket.close()
	
	predecessor_socket = socket.socket()
	predecessor_socket.connect((thisnode.ip,thisnode.predecessor))
	predecessor_socket.send(str("Bye. I am your successor and I am leaving.").encode())
	message = str(predecessor_socket.recv(1024).decode()) 
	predecessor_socket.send(str(thisnode.port).encode())#Okay tell me your port
	finalresponse = str(predecessor_socket.recv(1024).decode())
	print(finalresponse)
	if finalresponse == "Please send me your successor before leaving":
		predecessor_socket.send(str(thisnode.successor).encode())
	predecessor_socket.close()
	os._exit(0)

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

def printfingertable(thisnode):
	print(thisnode.fingertable)

def downloadfile(thisnode, filename, filehash):
	pass

def refresh(thisnode, anotherport):
	pass


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
			askforpred = anotherclient.recv(1024).decode()
			if askforpred == "Please send me port of your predecessor":
				anotherclient.send(str(thisnode.predecessor).encode())
				responsetosendingpredessor = anotherclient.recv(1024).decode()
				if responsetosendingpredessor == "Could easily adjust between the predecessor and the port.":
					print("The port has been added to the DHT")
				else:
					anotherclient.send(str(thisnode.successor).encode())
	elif responsefromclient == "Bye. I am your predecessor and I am leaving.":
		anotherclient.send("First, tell me your port number".encode())
		receiveleavingport = int(anotherclient.recv(1024).decode())
		if thisnode.predecessor == receiveleavingport and thisnode.successor == thisnode.predecessor:
			thisnode.predecessor = thisnode.port
			thisnode.successor = thisnode.port
			anotherclient.send("Okay nice to have you in our DHT. Bye".encode())
		else:
			anotherclient.send("Please send me your predecessor before leaving".encode())
			predecessorofpredecessor = int(anotherclient.recv(1024).decode())
			thisnode.predecessor= predecessorofpredecessor
		print("Node with port number ",receiveleavingport, " has left")
	elif responsefromclient == "Bye. I am your successor and I am leaving.":
		anotherclient.send("First, tell me your port number".encode())
		receiveleavingport = int(anotherclient.recv(1024).decode())
		if thisnode.successor == receiveleavingport and thisnode.successor == thisnode.predecessor:
			thisnode.predecessor = thisnode.port
			thisnode.successor = thisnode.port
			anotherclient.send("Okay nice to have you in our DHT. Bye".encode())
		else:
			anotherclient.send("Please send me your successor before leaving".encode())
			successorofsuccessor = int(anotherclient.recv(1024).decode())
			thisnode.successor= successorofsuccessor
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
			filename = str(input("Please enter file name: "))
			filehash = gethashfilename(filename)
			storefile(thisnode, filename, filehash)
		elif choice == 4:
			filename = str(input("Please enter file name: "))
			filehash = gethashfilename(filename)
			downloadfile(thisnode, filename, filehash)
		elif choice == 5:
			leaving(thisnode)
		else:
			continue

if __name__ == "__main__":
	# host = int(sys.argv[1])
	# port = int(sys.argv[2])
	host = '127.0.0.1'
	port = int(input("Please enter your port: "))
	#port = 1234
	thisnode = Node(host,port)
	#print(firstnode.hash)
	# print(firstnode.successor)
	mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	mysocket.bind((host,port))
	mysocket.listen(100) 

	while True:
		print("Press 1 if you have port number of another node: ")
		print("Press 2 if you do not have other port number: ")
		choice = int(input())
		if (choice == 1):
			anotherport = int(input("Please enter the port number of the other node: "))
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