import argparse
import cmd, sys
from p2p_net import P2P_network


def parse(arg):
  return tuple(map(str, arg.split()))


class netShell(cmd.Cmd):
  intro = "Welcome to p2p shell"
  prompt = ">> "
  file = None

  def __init__(self):
    cmd.Cmd.__init__(self)
    self.net = P2P_network()

  def do_connect(self, arg):
    self.net.connects(parse(arg)[0])

  def do_broadcast(self, arg):
    self.net.broadcast(parse(arg)[0])

  # need to provide both (self, arg) as argument
  # to avoid do_welcome() takes 1 positional argument but 2 were given error
  def do_info(self, arg):
    # print('welcome',self.net.peer_conn)
    self.net.info()

  # TODO
  def do_bye(self, arg):
    for t in self.net.thread_pool:
      t.join()
    # self.net.port = None
    print('close')
    # return True
    # print('dfd')
    raise SystemExit
    # print('close')


if __name__ == '__main__':
  netShell().cmdloop()





