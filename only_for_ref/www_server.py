# %%
# server

import socket
import time
from multiprocessing import Process

print(socket.AF_INET, socket.SOCK_STREAM)

# %%

machine_num = 5

host_name = socket.gethostname()
ip = socket.gethostbyname(host_name)

server_sockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(machine_num)]
  
print(host_name, ip)

# %%
ports = range(3000, 3000+machine_num)

def start_dev(i):
  while True:
    print('True', ports[i])
    client_socket, addr = server_sockets[i].accept()
    print('connection from', addr)

    # currentTime = time.ctime(time.time()) + '\n'
    msg = client_socket.recv(1024).decode()
    # client_socket.send(currentTime.encode('ascii'))
    client_socket.send(bytes(msg + ' oh god!', 'utf-8'))
    # client_socket.close()

for i in range(machine_num):
  server_sockets[i].bind((host_name, ports[i]))
  server_sockets[i].listen()

  p = Process(target=start_dev, args=(i,) )
  p.start()










