from p2p_python.config import C, V, Debug
from p2p_python.utils import setup_p2p_params
from p2p_python.client import PeerClient, ClientCmd
from p2p_python.tool.channel import Channel, ChannelCmd
from threading import Thread
import socket
import random
import logging
import time
import os

def get_logger(level=logging.DEBUG):
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter('[%(threadName)-10s] %(message)s')
  sh = logging.StreamHandler()
  sh.setLevel(level)
  sh.setFormatter(formatter)
  logger.addHandler(sh)
    
    
def f_already_bind(port):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  r = False
  try:
    s.bind(("127.0.0.1", port))
  except socket.error:
    print("Port is already in use")
    r = True
  s.close()
  return r
    
def broadcast_check(data):
  pk = data['pk'] if 'pk' in data else None
  debug = data['debug'] if 'debug' in data else None
  logging.info("broadcast data {} {} {}".format(data['type'], pk, debug))
  return True

def new_message(que):
  while True:
    data = que.get()
    logging.info("NewMsg {}".format(data))
 
 
def work():
  if f_already_bind(2000):
    port = random.randint(2001, 3000)
    sub_dir = 'test{}'.format(port)
    setup_p2p_params(network_ver=12345, p2p_port=port, p2p_accept=True, sub_dir=sub_dir)
  else:
    port = 2000
    setup_p2p_params(network_ver=12345, p2p_port=port, p2p_accept=True)

  Debug.P_EXCEPTION = True
  get_logger(level=logging.DEBUG)
  pc = PeerClient()
  pc.start()
  pc.broadcast_check = broadcast_check

  if port != 2000:
    pc.p2p.create_connection(host='127.0.0.1', port=2000)
    ch = Channel(pc, ch='channel-yes')
    ch.start()
    ch.ask_join(pk='ff063a0f3e6c83c00444069b6bb9d4b3be439b76babfef268d4f18a2a393c213', message='no comment')
  else:
    ch = Channel(pc, ch='channel-yes', seed=b'hello?')
    ch.start()
    ch.create_channel()

  Thread(target=new_message, args=(ch.message_que.create(),), daemon=True).start()
  logging.info("PK=> {}".format(ch.ecc.pk))
  logging.info("Connect as {}".format(port))

  while True:
    try:
      cmd = input('>> ')
      exec("print("+cmd+")")
      # print(pc.p2p.user[0])
    except EOFError:
      break
    except Exception as e:
      print(e)
 
work()





