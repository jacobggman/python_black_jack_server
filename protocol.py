import struct
from enum import Enum, auto, unique
import logging
import json

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



class Code:
    def to_json(self):
        fields = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        dictionary = dict()
        for field in fields:
            dictionary[field] = getattr(self, field)
        return json.dumps(dictionary)

    def get_code(self) -> Enum:
        pass

    @classmethod
    def from_json(cls, j: str):
        return_class = cls()
        json_dictionary = json.loads(j)
        args = return_class.get_args()
        for name, type in args:
            if name in json_dictionary:
                value = json_dictionary[name]
                if type(value) != type:
                    return "type error"
                setattr(return_class, name, value)
            else:
               if not type.optional:
                   return "non optional error"
            json_dictionary[name] = type
        return return_class

    def get_args(self):
        all_fields = map(lambda name: (name, getattr(self, name)), dir(self))
        return filter(lambda name_type: isinstance(name_type[1], ArgType), all_fields)

    def get_docs(self):
        code = self.get_code()
        args = list(self.get_args())
        return_str = code.name + "\n"
        return_str += f"code: {code.value}\n"
        return_str += "\nargs:\n" if len(args) != 0 else ""
        for name, var in args:
            return_str += f'name: {name}\n'
            return_str += f'{var.docs}\n'
            return_str += f'type: "{var.type.__name__}"\n'
            return_str += f'is optional: {var.optional}\n\n'
        return return_str


class ArgType:
    def __init__(self, type, docs, optional=False):
        self.type = type
        self.docs = docs
        self.optional = optional

class GET_CHAT(Code):
    origin = ArgType(str, "The username who send this message")
    message =  ArgType(str, "What the message that this username send")

    def get_code(self):
        return Codes.GET_CHAT

class Protocol:
    def __init__(self):
        self.codes = dict()
        self.last_index = 0

    def add_code_message(self, code=None):
        if code is None:
            pass


message = GET_CHAT()
print(message.get_docs())
print([type(x) for x in message.get_args()])

print(Codes.GET_CHAT.value)
