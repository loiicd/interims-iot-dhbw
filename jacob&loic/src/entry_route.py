from operators.conveyor_belt_operator import ConveyorBeltOperator
from operators.turn_table_operator import TurnTableOperator#
from operators.sensor_operator import SensorOperator
from io_extension import IOExtension
from typing import Dict, Union


class EntryRoute:
  def __init__(self, io_extension: IOExtension, operators: Dict[str, Union[ConveyorBeltOperator, TurnTableOperator, SensorOperator]]):
    self.io = io_extension
    self.operators = operators

  def initialize(self):
    """ Initialize the entry route """
    for operator in self.operators.values():
      operator.initialize()

  def moveBox(self):
    """ Move a box through the entry route """

    if (self.operators["sensor_1"].getState()):
      self.operators["conveyor_belt_1"].start()  
    else:
      print("No box detected on sensor 1")

    while (self.operators["sensor_5"].getState() or self.operators["sensor_6"].getState() or self.operators["sensor_7"].getState()):
      self.operators["conveyor_belt_3"].start()