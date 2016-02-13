from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import socket
import sys
import select
from os import urandom
import pickle

#globals
SIZE = 4096
BLOCK_SIZE = 16

#CHANGE WHEN ADDING REST OF INPUT ARGS
if len(sys.argv) < 3:
	print 'ERROR: not enough arguments'
	sys.exit()


#handle user inputs
host, port = sys.argv[1], int(sys.argv[2])
if ((port < 1024) or (port > 49151)):
	print 'ERROR: invalid port'
	sys.exit

#generate rsa key pair ans save to files
rsa_keys = RSA.generate(2048)
pubkey = rsa_keys.publickey().exportKey("PEM")
with open('c_pubkey.pem', 'w') as f:
	f.write(pubkey)
privkey = rsa_keys.exportKey("PEM")
with open('c_privkey.pem', 'w') as f:
	f.write(privkey)

key = 'a1b2c3d4e5f6g7h9' #sys.argv[3]
if len(key) != 16:
	print 'ERROR: password not 16 characters'
	sys.exit()

fname = 'file1.txt' #sys.argv[4]
ename = 'en' + fname

def encrypt_key():
	with open('s_pubkey.pem', 'r') as f:
		k = f.read()
		server_key = RSA.importKey(k)
	encrypted = server_key.encrypt(key, 16)
	return encrypted

#set up AES encryption
iv = urandom(BLOCK_SIZE)
mode = AES.MODE_CBC

def encrypt_file():
	encryptor = AES.new(key, mode, iv)
	with open(fname, 'rb') as f:
		plaintext = f.read()
	S = len(plaintext)
	L = S % BLOCK_SIZE
	if L < 16:
		plaintext+=' '*(16-L)
	length = str(S) + ' '*(16-len(str(S)))
	ciphertext = length + iv
	ciphertext += encryptor.encrypt(plaintext)
	return ciphertext

def hash_file():
	with open(fname, 'rb') as f:
		plaintext = f.read()
	h = SHA256.new(plaintext)
	print h.hexdigest()
	return h

def encrypt_hash(hash):
	with open('c_privkey.pem', 'r') as f:
		pk = f.read()
		pk = RSA.importKey(pk)
	enhash = pk.encrypt(hash.hexdigest(), 32)
	return enhash
"""
def decrypt_hash(enc):
	with open('c_privkey.pem', 'r') as f:
		pk = f.read()
		pk = RSA.importKey(pk)
	dehash = pk.decrypt(enc)
	return dehash

h = hash_file()
x = encrypt_hash(h)
print x
y = decrypt_hash(x)
print y

"""
#set up client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#try to connect to server
try:
	print "connecting..."
	client.connect((host, port))
except:
	print "no server on host/port"
	sys.exit()

sent = False

#handle data sent from server
while 1:
	sockets = [sys.stdin, client]
	read, write, error = select.select(sockets, [], [])
	try:
		for sock in read:
			if sock == client:
				data = sock.recv(SIZE)
				if data:
					print data
					if sent == False:
						sock.send('key')
						ek = encrypt_key()
						ek = pickle.dumps(ek)
						sock.send(ek)
						ctxt = encrypt_file()
						sock.send('file')
						sock.send(ctxt)
						sock.send('signature')
						h = hash_file()
						enchash = encrypt_hash(h)
						print enchash
						enchash = pickle.dumps(enchash)
						sock.send(enchash)
						sent == True

				#exit if server quit
				else:
					print "server disconnected"
					sys.exit()
			#send data to server
			else:
				msg = sys.stdin.readline()
				if msg:
					client.send(msg)

	#catch crtl-c interrupts
	except (KeyboardInterrupt, SystemExit):
		client.send('bye')
		client.close()
		sys.exit()

