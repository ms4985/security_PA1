from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import socket
import sys
import select
from os import urandom

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

key = 'a1b2c3d4e5f6g7h8' #sys.argv[3]
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

#function for encrypting file using AES in CBC mode
def encrypt_file():
	encryptor = AES.new(key, mode, IV=iv)
	
	#read file in rb mode
	with open(fname, 'rb') as f:
		#open file to write encrypted file in wb mode
		with open(ename, 'wb') as e:
			#prepend the iv string to the ciphertext
			e.write(iv)
			stop = False
			while stop == False:
				segment = f.read(BLOCK_SIZE)
				#check if reached EOF
				if len(segment) == 0:
					stop = True
				#check if we need to pad the last segment
				elif len(segment) < 16:
					segment += ' '*(16-len(segment))
				e.write(encryptor.encrypt(segment))

#set up client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#try to connect to server
try:
	print "connecting..."
	client.connect((host, port))
except:
	print "no server on host/port"
	sys.exit()

def send_file(sock):
	with open(ename, 'rb') as f:
		data = f.read(SIZE)
		sock.send(data)
	print 'done sending'

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
						sock.send(encrypt_key()[0])
						encrypt_file()
						sock.send('file')
						send_file(sock)
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

