from chat_example.codes import Codes
from jsock.code import Code
from jsock.arg_type import ArgType


class Hi(Code):
    def get_code(self):
        return Codes.HI
    
    def get_description(self) -> str:
        return "Hello to the client who want to login"

    def who_send(self) -> str:
        return "Server"
    
    def possible_responses(self):
        return [Name]
    

class Name(Code):
    name = ArgType(str, "The username to login")

    def get_code(self):
        return Codes.NAME

    def get_description(self) -> str:
        return "set the name for the login"

    def who_send(self) -> str:
        return "Client"

    def possible_responses(self):
        return [OkName, InvalidName]


class OkName(Code):
    def get_code(self):
        return Codes.OK_NAME

    def get_description(self) -> str:
        return "When the user login with this username"

    def who_send(self) -> str:
        return "Server"


class InvalidName(Code):
    info = ArgType(str, "Why the name is invalid")

    def get_code(self):
        return Codes.INVALID_NAME

    def get_description(self) -> str:
        return "When the user login with wrong username"

    def who_send(self) -> str:
        return "Server"

    def possible_responses(self):
        return [Name]
      
        
class EchoChat(Code):
    message = ArgType(str, "The message to send")
    
    def get_code(self):
        return Codes.ECHO_CHAT

    def get_description(self) -> str:
        return "When user send message to all users"

    def who_send(self) -> str:
        return "Client"
       
       
class GetChat(Code):
    message = ArgType(str, "The message that get send")
    user_name = ArgType(str, "The username who send this message")
    
    def get_code(self):
        return Codes.GET_CHAT
    
    def get_description(self) -> str:
        return "When user send message"

    def who_send(self) -> str:
        return "Server"


class Disconnect(Code):
    name = ArgType(str, "The username who disconnect")

    def get_code(self):
        return Codes.DISCONNECT

    def get_description(self) -> str:
        return "When user leave the chat"

    def who_send(self) -> str:
        return "Server"


class Connecting(Code):
    name = ArgType(str, "The username who connected")

    def get_code(self):
        return Codes.CONNECTING

    def get_description(self) -> str:
        return "When user connect to the chat"

    def who_send(self) -> str:
        return "Server"
