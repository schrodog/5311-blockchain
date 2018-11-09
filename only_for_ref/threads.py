import sys
import threading
import time
import logging

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        print( "base init", file=sys.stderr )
        super(StoppableThread, self).__init__()
        self._stopper = threading.Event()          
        # ! must not use _stop

    def stopit(self):                              
      #  (avoid confusion)
        print( "base stop()", file=sys.stderr )
        self._stopper.set()                        
        # ! must not use _stop

    def stopped(self):
        return self._stopper.is_set()              
        # ! must not use _stop


class datalogger(StoppableThread):
    """
    """

    import time

    def __init__(self, outfile):
      """
      """
      StoppableThread.__init__(self)
      self.outfile = outfile
      print( "thread init", file=sys.stderr )

    def run(self):
      """
      """
      print( "thread running", file=sys.stderr )
      while not self.stopped():
        print( self.outfile , file=sys.stderr)
        time.sleep(0.33)
      print( "thread ending", file=sys.stderr )


test = datalogger("test.txt")
test.start()
time.sleep(3)
logging.debug("stopping thread")
test.stopit()                                      #  (avoid confusion)
logging.debug("waiting for thread to finish")
test.join()