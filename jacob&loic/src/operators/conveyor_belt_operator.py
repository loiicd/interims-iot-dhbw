from enum import Enum
from io_extension import IOExtension


class ConveyorBeltOperator:
  def __init__(self, io_extension: IOExtension, length: str, port: int):
    self.io = io_extension
    self.port = port
    self.spin: bool = False

  def initialize(self):
    """ Initialize the operator """
    self.stop()

  def start(self):
    """ Start spinning motion of the operator """
    self.spin = True
    # self.io.set_port(0, 0, True)

  def stop(self):
    """ Stop spinning motion of the operator """
    self.spin = False
    # self.io.set_port(0, 0, True)