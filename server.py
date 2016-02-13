from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import socket
import sys
import select
import pickle

#globals
SIZE = 4096
BLOCK_SIZE = 16
connections = []
aes_mode = AES.MODE_CBC

#handle user input
if len(sys.argv) != 3:
	print 'ERROR: not enough arguments'
	sys.exit()

host, port = '', int(sys.argv[1])
if ((port < 1024) or (port > 49151)):
	print 'ERROR: invalid port'
	sys.exit()

mode = sys.argv[2]
if ((mode != 't') and (mode != 'u')):
	print 'ERROR: invalid mode'
	sys.exit()

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
#client sends a keyword first to the server
#then the server responds accordingly with the correct helper fn
def handle_client(sock, address):
	try:
		data = sock.recv(SIZE)
		#client has exited so cleanup
		if data == 'bye':
			connections.remove(sock)
			sock.close()
			print 'client disconnected'
		#client is about to send the key
		if data == 'key':
			handle_key(sock)
		#client is about to send the file
		if data == 'file':
			handle_file(sock)
		#client is about to send the signature
		if data == 'signature':
			handle_sig()
	except:
		#no data received by client so move on
		pass

def handle_key(sock):
	data = sock.recv(SIZE)
	data = pickle.loads(data)
	global KEY
	with open('s_privkey.pem', 'r') as f:
		p = f.read()
		pk = RSA.importKey(p)
	KEY = pk.decrypt(data)

def handle_file(sock):
	ctxt = sock.recv(SIZE)
	size = ctxt[:BLOCK_SIZE]
	iv = ctxt[BLOCK_SIZE:BLOCK_SIZE*2]
	ctxt = ctxt[BLOCK_SIZE*2:]
	decryptor = AES.new(KEY, aes_mode, iv)
	global plain
	if mode == 'u':
		with open('fakefile', 'rb') as f:
			ctxt = f.read()
	plain = decryptor.decrypt(ctxt)
	plain = plain[:int(size)]
	with open('decryptedfile', 'wb') as f:
		f.write(plain)

def handle_sig():
	data = sock.recv(SIZE)
	data = pickle.loads(data)
	with open('c_privkey.pem', 'r') as f:
		pk = f.read()
		pk = RSA.importKey(pk)
	dehash = pk.decrypt(data)
	h = SHA256.new(plain)
	if (h.hexdigest() == dehash):
		print 'Verification Passed'
	else:
		print 'Verficiation Failed'
		

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
				print 'client connected'
			else:
				try:
					handle_client(socket, address)
				except:
					sock.close()

except (KeyboardInterrupt, SystemExit):
	print "\nserver shutting down..."
	server.close()
	sys.exit()
