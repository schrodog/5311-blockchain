import argparse
import cmd, sys
from p2p_net import P2P_network
from multiprocessing import Process

def parse(arg):
  return tuple(map(str, arg.split()))


class netShell(cmd.Cmd):
  intro = "Welcome to p2p shell"
  prompt = ">> "
  file = None

  def __init__(self):
    cmd.Cmd.__init__(self)
    self.main = Process(target=self.__start, args=())
    self.main.start()

  def __start(self):
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
    # print(self.net.thread_pool)
    # for t in self.net.thread_pool:
    #   print(t)
    #   t.stop()
    #   t.join()
    self.main.join()

    print('close')
    raise SystemExit


if __name__ == '__main__':
  netShell().cmdloop()





