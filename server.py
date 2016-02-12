from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import socket
import sys
import select

#globals
SIZE = 4096
BLOCK_SIZE = 16
connections = []
mode = AES.MODE_CBC

#handle user input
host, port = '', int(sys.argv[1])
if ((port < 1024) or (port > 49151)):
	print 'ERROR: invalid port'
	sys.exit

#generate rsa key pairs and save to files
rsa_keys = RSA.generate(2048)
pubkey = rsa_keys.publickey().exportKey("PEM")
with open('s_pubkey.pem', 'w') as f:
	f.write(pubkey)
privkey = rsa_keys.exportKey("PEM")
with open('s_privkey.pem', 'w') as f:
	f.write(privkey)

#set up server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
print "server is running on: ", socket.gethostbyname(socket.gethostname())
server.listen(5)
print "server listening for clients..."
connections.append(server)

#handles receiving data from the client
def handle_client(sock, address):
	try:
		try:
			data = sock.recv(SIZE)
			if data:
				print data
			#client has exited so cleanup
			if data == 'bye':
				connections.remove(sock)
				sock.close()
			#client is about to send the key
			if data == 'key':
				handle_key(sock)
			#client is about to send the file
			if data == 'file':
				handle_file(sock)
				decrypt_file()
		finally:
			print 'handled client'
	except:
		pass

def handle_key(sock):
	data = sock.recv(SIZE)
	global KEY
	KEY = privkey.decrypt(data)

def handle_file(sock):
	with open('encfile', 'wb') as f:
		data = sock.recv(SIZE)
		f.write(data)
	print 'received file'

def decrypt_file():
	with open('encfile', 'rb') as e:
		iv = e.read(BLOCK_SIZE)
		decryptor = AES.new(KEY, mode, IV=iv)
		with open('decfile', 'wb') as d:
			stop = False
			while stop == False:
				segment = e.read(BLOCK_SIZE)
				if len(segment) == 0:
					stop = True
				d.write(decryptor.decrypt(segment))	

def close(socket):
	print 'close'
	connections.remove(socket)
	socket.close()

try:
	while 1:
		read, write, error = select.select(connections, [], [])
		for sock in read:
			if sock == server:
				socket, address = server.accept()
				socket.sendto("connected!", address)
				connections.append(socket)
			else:
				try:
					handle_client(socket, address)
				except:
					sock.close()

except (KeyboardInterrupt, SystemExit):
	print "\n server shutting down..."
	server.close()
	sys.exit()
