import socket
from protocol import Message, Codes
import threading
import json

def listen(s):
    try:
        message = Message.format(s.recv(1024))
        if message.code == Codes.GET_CHAT:
            my_dict = json.loads(message.data)
            print(f"{my_dict['origin']}: {my_dict['message']}")
        elif message.code == Codes.CONNECTING:
            print(f"{message.data} connect")
        elif message.code == Codes.DISCONNECT:
            print(f"{message.data} disconnect")
        else:
            print(message)
    except Exception as e:
        print(e)

def main():
    s = socket.socket()
    s.connect(('127.0.0.1', 8200))

    print("N:", Message.format(s.recv(1024)).data)
    invalid_name = True
    while invalid_name:
        str = input("S: ")
        if str == "Bye" or str == "bye":
            return s.close()

        msg = Message(Codes.NAME, str)
        s.send(msg.to_bytes())
        message = Message.format(s.recv(1024))
        if message.code == Codes.OK_NAME:
            invalid_name = False
        print("N:", message.data)

    threading.Thread(target=listen, args=(s,)).start()
    while True:
        str = input("S: ")
        if str == "Bye" or str == "bye":
            return s.close()
        msg = Message(Codes.ECHO_CHAT, str)
        s.send(msg.to_bytes())


if __name__ == '__main__':
    main()
