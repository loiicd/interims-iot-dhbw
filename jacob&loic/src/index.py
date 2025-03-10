from io_extension import IOExtension
from operators.conveyor_belt_operator import ConveyorBeltOperator
from operators.turn_table_operator import TurnTableOperator
from entry_route import EntryRoute
from mqtt_subscriber import MqttSubscriber


io = IOExtension()

operators = {
  "conveyor_belt_1": ConveyorBeltOperator(io, "short", 0),
  "conveyor_belt_2": ConveyorBeltOperator(io, "short", 0),
  "conveyor_belt_3": ConveyorBeltOperator(io, "short", 0),
  "conveyor_belt_4": ConveyorBeltOperator(io, "large", 0),
  "turn_table": TurnTableOperator(io, 0),
}

entryRoute = EntryRoute(io, operators)
entryRoute.initialize()
MqttSubscriber(entryRoute)