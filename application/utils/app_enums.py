

# Define TokenType Enum
from enum import Enum


class EnumTokenType(Enum):
    BUS_LINE = "BUS_LINE"
    BUS_DRIVER = "BUS_DRIVER"

class EnumBusVehicleServiceStatus(Enum):
    ON = "ON"
    OFF = "OFF"