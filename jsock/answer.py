import logging
from . import Errors


class Answer:
    _error: Errors
    _value: any
    check_error: bool

    def __init__(self):
        self.check_error = False

    def is_error(self):
        self.check_error = True
        return self._error is not None

    def error(self):
        return self._error

    def value(self):
        if not self.check_error:
            logging.critical("Not check error!")
        return self._value

    @classmethod
    def from_error(cls, error):
        a = cls()
        a._error = error
        a._value = None
        return a

    @classmethod
    def from_value(cls, value):
        a = cls()
        a._error = None
        a._value = value
        return a
