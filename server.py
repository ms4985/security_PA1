import Crypto
import socket
import sys
import select

SIZE = 4096
connections = []
host, port = '', int(sys.argv[1])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
print "server is running on: ", socket.gethostbyname(socket.gethostname())
server.listen(5)
print "server listening for clients..."
connections.append(server)

def handle_client(sock, address):
	print 'handle client'
	sock.sendto("enter password", address)
	password = sock.recv(SIZE)
	print password


try:
	while 1:
		read, write, error = select.select(connections, [], [])
		for sock in read:
			if sock == server:
				socket, address = server.accept()
				socket.sendto("connected!", address)
				handle_client(socket, address)
			else:
				print 'in else block'

except (KeyboardInterrupt, SystemExit):
	print "\n server shutting down..."
	server.close()
	sys.exit()
