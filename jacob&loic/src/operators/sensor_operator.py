from io_extension import IOExtension


class SensorOperator:
  def __init__(self, io_extension: IOExtension, port: int):
    self.io = io_extension
    self.port = port
    self.state: bool = False

  def getState(self) -> bool:
    return self.state