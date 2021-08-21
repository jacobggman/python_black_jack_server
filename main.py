import socket
import threading
from protocol import Codes, Message
from collections import deque
from limited_size_dict import LimitedSizeDict
from concurrent.futures import ThreadPoolExecutor

PORT = 1337
LISTEN_NUM = 50
AWAIT_LIMIT_NUM = 100
AWAIT_PER_CODE_LIMIT_NUM = 100


class Client:
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address


class InvalidProtocol(Exception):
    pass

# TODO: make a lib for socket server in python

# TODO: add on await failed (disconnected)
# TODO: delete unuse messages
# TODO: improve message read (first read code and len)
# TODO: do on code and on socket code
# TODO: make the protocol make automatic
# TODO: config the server how I like (return format error, auto correct and so on)
# TODO: make tls
# TODO: add typing to the function that the user use




class ThreadedServer(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self._host, self._port))

        self._input_lock = threading.Lock()
        self._input_cv = threading.Condition(self._input_lock)
        self._input_queue = deque()
        self._input_callback = dict()

        self._input_awaits = LimitedSizeDict(size_limit=AWAIT_LIMIT_NUM)
        self._await_lock = threading.Lock()
        self._await_cv = threading.Condition(self._await_lock)

        self._on_disconnect_dict = dict()
        self._on_connect = None

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

    def await_for_response(self, client, code):
        with self._await_cv:
            while (client, code) not in self._input_awaits:
                self._await_cv.wait()
            n = self._input_awaits[(client, code)]
            del self._input_awaits[(client, code)]
            return n

    # code, message
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
                            self._input_awaits[(client, message.code)] = message
                            self._await_cv.notify_all()

    def _add_to_queue(self, client, message):
        with self._input_cv:
            self._input_queue.append((client, message))
            self._input_cv.notify_all()

    def _on_listen_to_client(self, client):
        # TODO: fix the read of the size

        size = 1024
        while True:
            try:
                data = client.sock.recv(size)
                msg = Message.format(data)
                if msg.code == Codes.LOCAL_FORMAT_ERROR:
                    raise InvalidProtocol('Client disconnected')

                self._add_to_queue(client, msg)
                # msg.code = Codes.PONG
                # client.send(msg.to_bytes())

            except InvalidProtocol as e: # TODO: to not kick
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


if __name__ == "__main__":
    server = ThreadedServer('', PORT)
    server.set_on_connector(lambda x: print("hi!!"))
    server.start()
    while True:
        input()




