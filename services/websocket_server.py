# encoding: utf-8

from tornado import websocket, web
import json
import zmq
import jwt

import collections

from cesium_app.app_server import load_config
secret = load_config()['app:secret-key']

if secret is None:
    raise RuntimeError('We need a secret key to communicate with the server!')

ctx = zmq.Context()


class WebSocket(websocket.WebSocketHandler):
    sockets = collections.defaultdict(set)
    _zmq_stream = None

    def __init__(self, *args, **kwargs):
        websocket.WebSocketHandler.__init__(self, *args, **kwargs)

        if WebSocket._zmq_stream is None:
            raise RuntimeError("Please install a stream before instantiating "
                               "any websockets")

        self.authenticated = False
        self.auth_failures = 0
        self.max_auth_fails = 3
        self.username = None

    @classmethod
    def install_stream(cls, stream):
        cls._zmq_stream = stream

    @classmethod
    def subscribe(cls, username):
        cls._zmq_stream.socket.setsockopt(zmq.SUBSCRIBE,
                                          username.encode('utf-8'))

    @classmethod
    def unsubscribe(cls, username):
        cls._zmq_stream.socket.setsockopt(zmq.UNSUBSCRIBE,
                                          username.encode('utf-8'))

    def check_origin(self, origin):
        return True

    def open(self):
        self.request_auth()

    def on_close(self):
        sockets = WebSocket.sockets

        if self.username is not None:
            try:
                sockets[self.username].remove(self)
            except KeyError:
                pass

            # If we are the last of the user's websockets, since we're leaving
            # we unsubscribe to the message feed
            if len(sockets[self.username]) == 0:
                WebSocket.unsubscribe(self.username)

    def on_message(self, auth_token):
        self.authenticate(auth_token)
        if not self.authenticated and self.auth_failures < self.max_auth_fails:
            self.request_auth()

    def request_auth(self):
        self.auth_failures += 1
        self.send_json(action="AUTH REQUEST")

    def send_json(self, **kwargs):
        self.write_message(json.dumps(kwargs))

    def authenticate(self, auth_token):
        try:
            token_payload = jwt.decode(auth_token, secret)
            username = token_payload['username']

            self.username = username
            self.authenticated = True
            self.auth_failures = 0
            self.send_json(action='AUTH OK')

            # If we are the first websocket connecting on behalf of
            # a given user, subscribe to the feed for that user
            if len(WebSocket.sockets[username]) == 0:
                WebSocket.subscribe(username)

            WebSocket.sockets[username].add(self)

        except jwt.DecodeError:
            self.send_json(action='AUTH FAILED')
        except jwt.ExpiredSignatureError:
            self.send_json(action='AUTH FAILED')

    @classmethod
    def heartbeat(cls):
        for username in cls.sockets:
            for socket in cls.sockets[username]:
                socket.write_message(b'<3')

    # http://mrjoes.github.io/2013/06/21/python-realtime.html
    @classmethod
    def broadcast(cls, data):
        username, payload = [d.decode('utf-8') for d in data]

        for socket in cls.sockets[username]:
            print('[WebSocket] Forwarding message to', username)
            socket.write_message(payload)


if __name__ == "__main__":
    PORT = 64000
    LOCAL_OUTPUT = 'ipc:///tmp/message_flow_out'

    import zmq

    # https://zeromq.github.io/pyzmq/eventloop.html
    from zmq.eventloop import ioloop, zmqstream
    ioloop.install()

    sub = ctx.socket(zmq.SUB)
    sub.connect(LOCAL_OUTPUT)

    print('[websocket_server] Broadcasting {} to all websockets'.format(LOCAL_OUTPUT))
    stream = zmqstream.ZMQStream(sub)
    WebSocket.install_stream(stream)
    stream.on_recv(WebSocket.broadcast)

    server = web.Application([
        (r'/websocket', WebSocket),
    ])
    server.listen(PORT)

    # We send a heartbeat every 45 seconds to make sure that nginx
    # proxy does not time out and close the connection
    ioloop.PeriodicCallback(WebSocket.heartbeat, 45000).start()

    print('[websocket_server] Listening for incoming websocket connections on port {}'.format(PORT))
    ioloop.IOLoop.instance().start()
