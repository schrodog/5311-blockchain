from p2p_python.client import PeerClient, ClientCmd
from socket import AF_INET
from p2p_python.utils import setup_p2p_params

setup_p2p_params(network_ver=1000, p2p_port=4000, p2p_accept=True, sub_dir='user1', f_debug=True)

pc = PeerClient(f_local=True)
pc.start(f_stabilize=True)


while 1:
  



