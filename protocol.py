import struct
from enum import Enum, auto, unique
import logging

SIZE_OF_CODE = 2
SIZE_OF_DATA_LEN = 2
SIZE_OF_BYTE = 8


@unique
class Codes(Enum):
    LOCAL_FORMAT_ERROR = 0
    PING = auto()
    PONG = auto()
    CONNECT_TO_GAME = auto()
    FILLED_TO_CONNECT_TO_GAME = auto()
    UNKNOWN_KEY_CODE = auto()
    HI = auto()
    NAME = auto()
    OK_NAME = auto()
    INVALID_NAME = auto()
    ECHO_CHAT = auto()
    GET_CHAT = auto()
    DISCONNECT = auto()
    CONNECTING = auto()
    OVER_MAX = 65536


class Message:
    def __init__(self, code, data):
        self.code = code
        self.data = data

    def __repr__(self):
        return f"Message({self.code}, {repr(self.data)})"

    @classmethod
    def format(cls, raw_msg: bytes):
        if raw_msg is None or len(raw_msg) < SIZE_OF_CODE + SIZE_OF_DATA_LEN:
            return cls.error()
        code_int = struct.unpack_from('>H', raw_msg)[0]
        code = Codes(code_int)
        size = struct.unpack_from('>H', raw_msg, SIZE_OF_CODE)[0]
        data = raw_msg[SIZE_OF_CODE * 2:SIZE_OF_CODE * 2 + size]
        return cls(code, data.decode())

    @classmethod
    def error(cls):
        return cls(Codes.LOCAL_FORMAT_ERROR, "")

    def to_bytes(self):
        if self.code.value > 2 ** (SIZE_OF_CODE * SIZE_OF_BYTE) - 1:
            logging.critical("code is behind the limit of the code size")
            return b'0'

        len_data = len(self.data)
        if len_data > 2 ** (SIZE_OF_DATA_LEN * SIZE_OF_BYTE) - 1:
            logging.critical("the size of the data is behind the limit of the data size")
            return b'0'

        code_bytes = struct.pack('>H', self.code.value)
        size_bytes = struct.pack('>H', len(self.data))
        byte_message = bytes(self.data, 'utf-8')
        return code_bytes + size_bytes + byte_message
