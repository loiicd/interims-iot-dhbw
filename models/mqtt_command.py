from enum import Enum


class Operations(Enum):
    DESTORE = 0
    STORE = 1
    REARRANGE = 2
    STORE_RANDOM = 3
    DESTORE_RANDOM = 4
    STORE_ASCENDING = 5
    DESTORE_ASCENDING = 6
    DESTORE_OLDEST = 7
    HEALTH = 8


class MqttCommand:
    operation: Operations
    x: int
    z: int
    x_new: int
    z_new: int

    def __init__(self, operation: str, x=-1, z=-1, x_new=-1, z_new=-1):
        """ based on the command, parameters are optional"""
        self.operation = Operations[operation]
        self.x = int(x)
        self.z = int(z)
        self.x_new = int(x_new)
        self.z_new = int(z_new)
