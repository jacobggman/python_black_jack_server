import socket
from protocol import Message, Codes

s = socket.socket()
s.connect(('127.0.0.1',1337))
while True:
    str = input("S: ")
    if (str == "Bye" or str == "bye"):
        break
    msg = Message(Codes.PING, str)
    s.send(msg.to_bytes())
    print("N:", Message.format(s.recv(1024)))
s.close()
