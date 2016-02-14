Megan Skrypek
ms4985
COMS w4180
Programming Assignment 1

RSA Key Generation:
the rsa keys were generated using the pycrypto library module Crypto.PublicKey.RSA
the key pairs were generated using 2048 bit modulus and written to separate files

To Run:
first generate the rsa keys by executing rsakeys.py
$ python rsakeys.py

then execute the server code, server.py, with the necessary arguments
$ python server.py [port number] [mode]

then execute the client code, client.py, with the necessary arguments
$ python client.py [ip address] [port number] [16 char AES key] [filename]

Additional Notes:
- the file used for encryption must be in the same directory (same for the fakefile)
- 'decrypedfile' only gets written to in trusted mode
- the rsa keys are generated and written to four separate files and the client and server have the names of those files hardcoded in
- client will exit on its own, but the server will only exit using 'crtl-c'
