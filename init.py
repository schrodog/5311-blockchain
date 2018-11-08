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
    self.net.connect(parse(arg))

  # need to provide both self, arg as argument
  # to avoid do_welcome() takes 1 positional argument but 2 were given error
  def do_welcome(self, arg):
    self.net.welcome()


if __name__ == '__main__':
  netShell().cmdloop()





