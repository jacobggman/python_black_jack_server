

class JsockException(Exception):
    pass


class AwaitError(JsockException):
    pass


class AwaitTimeout(AwaitError):
    pass


class AwaitLostConnection(AwaitError):
    pass


class ArgMessage(JsockException):
    pass


class MissingRequiredArg(ArgMessage):
    pass


class WrongTypeArg(ArgMessage):
    pass


class LocalFormatMessageError(JsockException):
    pass


class MessageFormatError(JsockException):
    pass
