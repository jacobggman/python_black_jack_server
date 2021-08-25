from jsock.protocol import Protocol
import chat_example
from chat_example import codes

proto = Protocol(chat_example)

print(proto.codes)
class_type = proto.get_class(codes.Codes.GET_CHAT)


print(class_type)









# GET_CHAT.get_code(None)
#
# print(message.get_docs())
# print([type(x) for x in message.get_args()])
#
# print(Codes.GET_CHAT.value)
