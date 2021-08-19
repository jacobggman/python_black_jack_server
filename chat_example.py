from main import ThreadedServer
from protocol import Codes, Message
import json


class ChatServer:
    def __init__(self, server: ThreadedServer, name):
        self.server = server
        self.server.set_on_connector(self.on_connect)
        self.clients = dict()
        self.name = name

    def start(self):
        self.server.start()

    def on_connect(self, client):
        hello_msg = Message(Codes.HI, f"Welcome to the chat server of {self.name}. Enter you`r name!")
        self.server.send_message(client, hello_msg)

        while True:
            response = self.server.await_for_response(client, Codes.NAME)
            if response.data == "":
                self.server.send_message(client, Message(Codes.INVALID_NAME, "Invalid name"))
                continue
            elif response.data in self.clients:
                self.server.send_message(client, Message(Codes.INVALID_NAME, "Used name!"))
                continue
            else:
                break

        self.server.send_message(client, Message(Codes.OK_NAME, f"Welcome {response.data}!"))
        client.name = response.data
        self.clients[response.data] = client

        self.server.set_on_message(client, Codes.ECHO_CHAT, self.on_send)
        self.server.set_on_disconnect(client, self.on_disconnect)

        self.echo(Message(Codes.CONNECTING, client.name), client)

    def on_disconnect(self, client):
        del self.clients[client.name]
        self.echo(Message(Codes.DISCONNECT, client.name))

    def echo(self, message, except_client=None):
        for client in self.clients:
            if self.clients[client] != except_client:
                print(f"send: {message.data} to {client}")
                self.server.send_message(self.clients[client], message)

    def on_send(self, client, message):
        message_dict = {"message": message.data, "origin": client.name}
        message = Message(Codes.GET_CHAT, json.dumps(message_dict))
        self.echo(message, client)

if __name__ == "__main__":
    server = ThreadedServer('', 8200)
    chat_server = ChatServer(server, "Jacob")
    chat_server.start()
    while True:
        input()
