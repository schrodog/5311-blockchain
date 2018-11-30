from argparse import ArgumentParser
import cmd, sys
from p2p_net import P2P_network
from multiprocessing import Process
from pprint import pprint

parser = ArgumentParser()
parser.add_argument("-u", "--user", dest="user", default="")
args = parser.parse_args()

def parse(arg):
  return tuple(map(str, arg.split()))


class netShell(cmd.Cmd):
  intro = "Welcome to blockchain"
  prompt = ">> "
  file = None

  def __init__(self):
    cmd.Cmd.__init__(self)
    self.__start()
    # self.net = None
    # self.main = Process(target=self.__start, args=(self.net,))
    # self.main.start()

  def __start(self):
    self.net = P2P_network(args.user)

  def do_connect(self, arg):
    self.net.connects(parse(arg)[0])

  def do_broadcast(self, arg):
    self.net.broadcast(parse(arg)[0])

  def do_mine(self, arg):
    self.net.mine()

  # need to provide both (self, arg) as argument
  # to avoid do_welcome() takes 1 positional argument but 2 were given error
  def do_info(self, arg):
    self.net.info()

  def do_selfblock(self, arg):
    pprint(self.net.blockchain.block_chain)

  def do_selfblockhashes(self, arg):
    pprint(self.net.blockchain.block_hashes)

  def do_getblock(self, arg):
    if len(arg) == 1:
      self.net.getBlockHashFromDest(parse(arg)[0])

  def do_getdata(self, arg):
    if len(arg) == 3:
      dest_peer_id, data_type, curr_hash = parse(arg)
      self.net.getDataByHash(dest_peer_id, data_type, curr_hash)
    else:
      print('please input [peer id, data type(block/tx), hash value]')

  def do_bye(self, arg):
    print('close')
    raise SystemExit


if __name__ == '__main__':
  netShell().cmdloop()





