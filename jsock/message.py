import struct
import logging
from errors import Errors

SIZE_OF_CODE = 2
SIZE_OF_DATA_LEN = 2
SIZE_OF_BYTE = 8


class MessageHeader:
    def __init__(self, code, size):
        self.code = code
        self.size = size

    def __repr__(self):
        return f"MessageHeader({self.code}, {self.size})"

    @staticmethod
    def get_size():
        return SIZE_OF_CODE + SIZE_OF_DATA_LEN

    @classmethod
    def format(cls, raw_msg: bytes, code_enum_type):
        if raw_msg is None or len(raw_msg) < SIZE_OF_CODE + SIZE_OF_DATA_LEN:
            return cls.error(Errors.LOCAL_FORMAT_ERROR)
        code_int = struct.unpack_from('>H', raw_msg)[0]
        code = code_enum_type.code_enum_type(code_int)
        size = struct.unpack_from('>H', raw_msg, SIZE_OF_CODE)[0]
        return cls(code, size)

    @classmethod
    def error(cls, error, size=0):
        return cls(error, size)

    def to_bytes(self):
        if self.code.value > 2 ** (SIZE_OF_CODE * SIZE_OF_BYTE) - 1:
            logging.critical("code is behind the limit of the code size")
            return b'0'

        if self.size > 2 ** (SIZE_OF_DATA_LEN * SIZE_OF_BYTE) - 1:
            logging.critical("the size of the data is behind the limit of the data size")
            return b'0'

        code_bytes = struct.pack('>H', self.code.value)
        size_bytes = struct.pack('>H', self.size)
        return code_bytes + size_bytes


class Message:
    def __init__(self, header: MessageHeader, data):
        self._header = header
        self.data = data

    def __repr__(self):
        return f"Message({repr(self._header)}, {repr(self.data)})"

    def get_code(self):
        return self._header.code

    @classmethod
    def format(cls, header: MessageHeader, format_data):
        data = format_data
        return cls(header, data.decode())

    @classmethod
    def error(cls, error: Errors, data=b""):
        return cls(MessageHeader.error(error), data)

    def to_bytes(self):
        byte_message = bytes(self.data.to_json(), 'utf-8')
        return self._header.to_bytes() + byte_message
