# client.py
import socket

# create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name and ip
host_name = socket.gethostname()
ip = socket.gethostbyname(host_name)
# client_socket.bind((host_name, 5000))

print('This host name is: ', host_name)
print('The host ip is: ', ip)

# set the port number
port = 3001

txt = input("pls enter: ")
client_socket.connect((ip, port))
client_socket.send(bytes(txt, 'utf-8'))

tm = client_socket.recv(1024)
print('The time is ', tm.decode())
client_socket.close()

















