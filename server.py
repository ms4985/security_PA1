from Crypto.Cipher import AES
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

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
print "server is running on: ", socket.gethostbyname(socket.gethostname())
server.listen(5)
print "server listening for clients..."
connections.append(server)

def handle_client(sock, address):
	try:
		try:
			data = sock.recv(SIZE)
			if data:
				print data
			if data == 'close':
				connections.remove(sock)
				sock.close()
			if data == 'file':
				handle_file(sock)
				decrypt_file()
		except:
			close(sock)
	except:
		pass

def handle_file(sock):
	with open('encfile', 'wb') as f:
		data = sock.recv(SIZE)
		f.write(data)
	print 'received file'

def decrypt_file():
	key = 'a1b2c3d4e5f6g7h8'
	with open('encfile', 'rb') as e:
		iv = e.read(BLOCK_SIZE)
		decryptor = AES.new(key, mode, iv)
		with open('decfile', 'wb') as d:
			stop = False
			while stop == False:
				segment = e.read(BLOCK_SIZE)
				if len(segment) == 0:
					stop == True
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
					close(sock)

except (KeyboardInterrupt, SystemExit):
	print "\n server shutting down..."
	server.close()
	sys.exit()
