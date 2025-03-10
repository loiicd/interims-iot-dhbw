from operators.conveyor_belt_operator import ConveyorBeltOperator
from operators.turn_table_operator import TurnTableOperator
from io_extension import IOExtension
from typing import Dict, Union


class EntryRoute:
  def __init__(self, io_extension: IOExtension, operators: Dict[str, Union[ConveyorBeltOperator, TurnTableOperator]]):
    self.io = io_extension
    self.operators = operators

  def initialize(self):
    """ Initialize the entry route """
    for operator in self.operators.values():
      operator.initialize()

  def moveBox(self):
    """ Move a box through the entry route """
    self.operators["conveyor_belt_1"].start()
    self.operators["conveyor_belt_2"].start()
    self.operators["conveyor_belt_3"].start()
    self.operators["conveyor_belt_4"].start()
    self.operators["conveyor_belt_1"].stop()
    self.operators["conveyor_belt_2"].stop()
    self.operators["conveyor_belt_3"].stop()
    self.operators["conveyor_belt_4"].stop()