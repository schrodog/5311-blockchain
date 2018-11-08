from p2p_python.client import PeerClient, ClientCmd
from socket import AF_INET
from p2p_python.utils import setup_p2p_params

setup_p2p_params(network_ver=1000, p2p_port=4001, p2p_accept=True, sub_dir='user2', f_debug=True)

pc = PeerClient(f_local=True)
pc.start(f_stabilize=True)

pc.p2p.create_connection(host='127.0.0.1', port=4000)





