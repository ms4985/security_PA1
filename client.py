from Crypto.Cipher import AES
import socket
import sys
import select

#globals
SIZE = 4096

#handle user inputs
host, port = sys.argv[1], int(sys.argv[2])
if ((port < 1024) or (port > 49151)):
	print 'ERROR: invalid port'
	sys.exit

key = 'a1b2c3d4e5f6g7h8'
if len(key) != 16:
	print 'ERROR: password not 16 characters'
	sys.exit()

fname = 'file1.txt'


#set up AES encryption
iv = 16 * '\x00'
mode = AES.MODE_CBC

#function for encrypting file using AES in CBC mode
def encrypt_file(fname, key):
	encryptor = AES.new(key, mode, IV=iv)
	text = 'a' * 64 
	print text
	ciphertext = encryptor.encrypt(text)
	print ciphertext

#set up client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#try to connect to server
try:
	print "connecting..."
	client.connect((host, port))
except:
	print "no server on host/port"
	sys.exit()

#handle data sent from server
while 1:
	sockets = [sys.stdin, client]
	read, write, error = select.select(sockets, [], [])
	try:
		for sock in read:
			if sock == client:
				data = sock.recv(SIZE)
				if data:
					sys.stdout.write(data)
					sys.stdout.write('\n* ')
					sys.stdout.flush()
				#exit if server quit
				else:
					print "server disconnected"
					sys.exit()
			#send data to server
			else:
				msg = sys.stdin.readline()
				if msg:
					client.send(msg)
				sys.stdout.write('* ')
				sys.stdout.flush()

	#catch crtl-c interrupts
	except (KeyboardInterrupt, SystemExit):
		sys.exit()
