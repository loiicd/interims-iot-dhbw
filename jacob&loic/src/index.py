from io_extension import IOExtension
from operators.conveyor_belt_operator import ConveyorBeltOperator
from operators.turn_table_operator import TurnTableOperator
from operators.sensor_operator import SensorOperator
from entry_route import EntryRoute
from mqtt_subscriber import MqttSubscriber


io = IOExtension()

operators = {
  "conveyor_belt_1": ConveyorBeltOperator(io, "short", 0),
  "conveyor_belt_2": ConveyorBeltOperator(io, "short", 0),
  "conveyor_belt_3": ConveyorBeltOperator(io, "short", 0),
  "conveyor_belt_4": ConveyorBeltOperator(io, "large", 0),
  "turn_table": TurnTableOperator(io, 0),
  "sensor_1": SensorOperator(io, 0),
  "sensor_2": SensorOperator(io, 0),
  "sensor_3": SensorOperator(io, 0),
  "sensor_4": SensorOperator(io, 0),
  "sensor_5": SensorOperator(io, 0),
  "sensor_6": SensorOperator(io, 0),
  "sensor_7": SensorOperator(io, 0),
  "sensor_8": SensorOperator(io, 0),
  "sensor_9": SensorOperator(io, 0),
}

entryRoute = EntryRoute(io, operators)
entryRoute.initialize()
MqttSubscriber(entryRoute)