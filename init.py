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

  def __start(self):
    self.net = P2P_network(args.user)

  def do_connect(self, arg):
    self.net.connects(parse(arg)[0])

  def help_connect(self):
    print('Description:\n\tConnect to TCP socket of another node by stating port number')
    print('Synopsis:\n\tconnect [port no]')

  # def do_broadcast(self, arg):
  #   self.net.broadcast(parse(arg)[0])

  def do_mine(self, arg):
    args = parse(arg)
    if len(args) == 2:
      self.net.mine({'dest_addr': args[0], 'value':args[1]})
    else:
      self.net.mine()

  def help_mine(self):
    print('Description:\n\tMine block once, can add transaction to block')
    print('Synopsis:\n\tmine (destination id) (value)')

  # need to provide both (self, arg) as argument
  # to avoid do_welcome() takes 1 positional argument but 2 were given error
  def do_info(self, arg):
    self.net.info()
  
  def help_info(self):
    print('Description:\n\tPrint information related to peer')
    print('Synopsis:\n\tinfo')


  def do_selfblock(self, arg):
    pprint(self.net.blockchain.block_chain)

  def help_selfblock(self):
    print('Description:\n\tPrint own blockchain of peer')
    print('Synopsis:\n\tselfblock')


  def do_transaction(self, arg):
    args = parse(arg)   # dest_addr, value
    if len(args) == 2:
      self.net.broadcastTransaction(args[0], args[1])
    else:
      print('Please input destination id, value')

  def help_transaction(self):
    print('Description:\n\tBroadcast transaction to peers, but not mining block itself, sender default to be the one initiate transaction')
    print('Synopsis:\n\ttransaction [destination id] [value]')


  # def do_selfblockhashes(self, arg):
  #   pprint(self.net.blockchain.block_hashes)

  def do_search(self, arg):
    self.net.getDataByHash(parse(arg)[0])

  def help_search(self):
    print('Description:\n\tSearch data of block according to hash, can be of block hash / transaction hash')
    print('Synopsis:\n\tsearch [hash]')


  # def do_getdata(self, arg):
  #   if len(arg) == 3:
  #     dest_peer_id, data_type, curr_hash = parse(arg)
  #     self.net.getDataByHash(dest_peer_id, data_type, curr_hash)
  #   else:
  #     print('please input [peer id, data type(block/tx), hash value]')

  def do_bye(self, arg):
    print('close')
    raise SystemExit

  def help_bye(self):
    print('Description:\n\tExit blockchain program')
    print('Synopsis:\n\tbye')


  def do_debug(self, arg):
    self.net.debug()
  
  def help_debug(self):
    print('Description:\n\tShow data for program debug')
    print('Synopsis:\n\tdebug')



if __name__ == '__main__':
  netShell().cmdloop()





