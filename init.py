import argparse
import cmd, sys
from p2p_net import P2P_network
from multiprocessing import Process
from pprint import pprint

def parse(arg):
  return tuple(map(str, arg.split()))


class netShell(cmd.Cmd):
  intro = "Welcome to p2p shell"
  prompt = ">> "
  file = None

  def __init__(self):
    cmd.Cmd.__init__(self)
    self.__start()
    # self.net = None
    # self.main = Process(target=self.__start, args=(self.net,))
    # self.main.start()

  def __start(self):
    self.net = P2P_network()

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

  def do_bye(self, arg):
    print('close')
    raise SystemExit


if __name__ == '__main__':
  netShell().cmdloop()





