from io_extension import IOExtension


class TurnTableOperator:
  def __init__(self, io_extension: IOExtension, port: int):
    self.io = io_extension
    self.port = port
    self.turn_clockwise = False
    self.turn_counter_clockwise = False

  def initialize(self):
    """ Initialize the operator """
    self.stop()

  def stop(self):
    """ Stop spinning motion of the operator """
    self.turn_clockwise = False
    self.turn_counter_clockwise = False
    # self.io.set_port(0, 0, False)
    # self.io.set_port(0, 1, False)