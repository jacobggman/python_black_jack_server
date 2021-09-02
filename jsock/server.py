import socket
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from jsock.protocol import Protocol
from jsock.message import MessageHeader, Message
from jsock.errors import Errors
from jsock.client import Client
from jsock.config import Config

PORT = 1337
LISTEN_NUM = 50
AWAIT_LIMIT_NUM = 1000

# JacobSocks
#
# Features:
# Multithreading
# Simple
# Customisable
# Auto documentation your API
# Error handling
# Get message by callbacks and by (self made) await (await per socket)
# Expandable

# How to use:
# Show code


class InvalidProtocol(Exception):
    pass


# TODO: make a lib for socket server in python

# TODO: Threw a exception
# TODO: make the config
# TODO: Make the chat server
# TODO: Upload to git and readme
# TODO: Finish the server
# TODO: + add on await failed (disconnected)
# TODO: + delete unuse messages
# TODO: do on code and on code socket function callbakcs (no necessary)
# TODO: + improve message read (first read code and len)
# TODO: += for adding function
# TODO: -= for removing function
# TODO: make the chat_example docs automatic
# TODO: DEBUG

# TODO: config the server how I like (return format error, auto correct and so on, encryption or not)
# (make the class first)
# TODO: make tls


class ThreadedServer(object):
    def __init__(self, config: Config, protocol: Protocol):
        self._config = config
        self._protocol = protocol
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self._config.host, self._config.port))

        self._input_lock = threading.Lock()
        self._input_cv = threading.Condition(self._input_lock)
        self._input_queue = deque()
        self._input_callback = dict()

        self._input_awaits = dict()
        self._await_lock = threading.Lock()
        self._await_cv = threading.Condition(self._await_lock)

        self._on_disconnect_dict = dict()
        self._on_connect = None

        self._await_socks = dict()
        # self.output_lock = threading.Lock()
        # self.output_cv = threading.Condition(self.output_lock)
        # self.output_queue = deque()

        self._output_executor = ThreadPoolExecutor()
        self._callbacks_executor = ThreadPoolExecutor()

    def start(self):
        threading.Thread(target=self._await_start).start()

    def _await_start(self):
        self._sock.listen(LISTEN_NUM)
        threading.Thread(target=self._get_message_listener).start()
        while True:
            client = Client(*self._sock.accept())
            # TODO: need "client.settimeout(120)" ?
            if self._on_connect is not None:
                self._callbacks_executor.submit(lambda: self._on_connect(client))
            threading.Thread(target=self._on_listen_to_client, args=(client,)).start()

    @staticmethod
    def _send(sock, message):
        sock.send(message.to_bytes())

    def set_on_disconnect(self, sock, func):
        if func is None:
            del self._on_disconnect_dict[sock]
        else:
            self._on_disconnect_dict[sock] = func

    def set_on_connector(self, func):
        self._on_connect = func

    def set_on_message(self, client, code, func):
        if func is None:
            del self._input_callback[(client, code)]
        else:
            print(func)
            self._input_callback[(client, code)] = func

    def send_message(self, client, message):
        func = lambda: self._send(client.sock, message)
        self._output_executor.submit(func)

    # TODO: remove size limit and add dict of requests and not save every message
    # TODO: timeout
    def await_for_response(self, client, code, timeout=None, config=None):
        with self._await_cv:
            self._input_awaits[(client, code)] = None
            if client not in self._await_socks:
                self._await_socks[client] = []
            self._await_socks[client].apppend(code)

            while self._input_awaits[(client, code)] is None:
                self._await_cv.wait()

            return_value = self._input_awaits[(client, code)]
            del self._input_awaits[(client, code)]

            self._await_socks[client].remove(code)

            if len(self._await_socks[client]) == 0:
                del self._await_socks[client]

            return return_value

    # sorter
    def _get_message_listener(self):
        while True:
            with self._input_cv:
                while len(self._input_queue) == 0:
                    self._input_cv.wait()
                while len(self._input_queue) != 0:
                    client, message = self._input_queue.pop()
                    # print(f"{client.sock} send: {message}")
                    # check if someone need the message of there is a callback
                    func = self._input_callback.get((client, message.code))
                    have_callback_code = func is not None
                    if have_callback_code:
                        self._callbacks_executor.submit(lambda: func(client, message))
                    else:
                        with self._await_cv:
                            if (client, message.code) in self._input_awaits:
                                self._input_awaits[(client, message.code)] = message
                                self._await_cv.notify_all()

    def _add_to_queue(self, client, message):
        with self._input_cv:
            self._input_queue.append((client, message))
            self._input_cv.notify_all()

    # TODO: don't listen to non use code
    def _on_listen_to_client(self, client):
        while True:
            try:
                header_data = client.sock.recv(MessageHeader.get_size())

                header = MessageHeader.format(header_data, self._config.code_enum_type)
                if header.code == Errors.LOCAL_FORMAT_ERROR:
                    raise InvalidProtocol('Client disconnected')

                data = client.sock.recv(header.get_size())
                class_type = self._protocol.get_class(header)
                if class_type is not None:
                    message = Message.format(header, class_type.from_json(data.decode()))
                    self._add_to_queue(client, message)

            except InvalidProtocol as e:  # TODO: to not kick
                print(e)
                client.sock.close()
                func = self._on_disconnect_dict.get(client)
                if func is not None:
                    self._callbacks_executor.submit(lambda: func(client))
                return False
            except OSError as e:
                print(e)
                client.sock.close()
                func = self._on_disconnect_dict.get(client)
                if func is not None:
                    self._callbacks_executor.submit(lambda: func(client))
                return False

    def _on_disconnect(self, client):
        with self._await_cv:
            if client in self._await_socks:
                for code in self._await_socks[client]:
                    self._input_awaits[(client, code)] = Message.error()
                del self._await_socks[client]
                self._await_cv.notify_all()

        client.sock.close()
        func = self._on_disconnect_dict.get(client)
        if func is not None:
            self._callbacks_executor.submit(lambda: func(client))

