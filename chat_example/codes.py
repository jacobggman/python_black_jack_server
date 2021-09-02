from enum import Enum, unique, auto


@unique
class Codes(Enum):
    HI = auto()
    NAME = auto()
    OK_NAME = auto()
    INVALID_NAME = auto()
    ECHO_CHAT = auto()
    GET_CHAT = auto()
    DISCONNECT = auto()
    CONNECTING = auto()
    OVER_MAX = 65536
