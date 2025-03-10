from io_extension import IOExtension
from operators.conveyor_belt_operator import ConveyorBeltOperator
from operators.turn_table_operator import TurnTableOperator
from entry_route import EntryRoute
from mqtt_subscriber import MqttSubscriber


io = IOExtension()

operators = {
  "conveyor_belt_1": ConveyorBeltOperator(io, 1, 0),
  "conveyor_belt_2": ConveyorBeltOperator(io, 3, 0),
  "conveyor_belt_3": ConveyorBeltOperator(io, 2, 0),
  "turn_table_1": TurnTableOperator(io, 0),
}

entryRoute = EntryRoute(io, operators)
entryRoute.init()
MqttSubscriber(entryRoute)