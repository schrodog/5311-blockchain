# client.py
import socket

# create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name and ip
host_name = socket.gethostname()
ip = socket.gethostbyname(host_name)

print('This host name is: ', host_name)
print('The host ip is: ', ip)

# set the port number
port = 3001

# connection to the host_name on the port, please change the ip address for the host
client_socket.connect((ip, port))

# Receiver no more than 1024 bytes
tm = client_socket.recv(100)
client_socket.close()
print('The time got form the server is %s' % tm.decode('ascii'))

















