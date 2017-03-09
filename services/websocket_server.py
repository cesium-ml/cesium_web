# encoding: utf-8

from tornado import websocket, web
import json
import zmq
import jwt

from cesium_app import config
secret = config.cfg['app']['secret-key']

ctx = zmq.Context()


# Could also use: http://aaugustin.github.io/websockets/


class WebSocket(websocket.WebSocketHandler):
    participants = set()

    def __init__(self, *args, **kwargs):
        websocket.WebSocketHandler.__init__(self, *args, **kwargs)

        self.authenticated = False
        self.auth_failures = 0
        self.max_auth_fails = 3
        self.username = None

    def check_origin(self, origin):
        return True

    def open(self):
        if self not in self.participants:
            self.participants.add(self)
            self.request_auth()

    def on_close(self):
        if self in self.participants:
            self.participants.remove(self)

            # do something here to unsubscribe

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
            self.username = token_payload['username']
            self.authenticated = True
            self.auth_failures = 0
            self.send_json(action='AUTH OK')

            # Do something here to subscribe

        except jwt.DecodeError:
            self.send_json(action='AUTH FAILED')
        except jwt.ExpiredSignatureError:
            self.send_json(action='AUTH FAILED')

    @classmethod
    def heartbeat(cls):
        for p in cls.participants:
            p.write_message(b'<3')

    # http://mrjoes.github.io/2013/06/21/python-realtime.html
    @classmethod
    def broadcast(cls, stream, data):
        username, payload = [d.decode('utf-8') for d in data]

        for p in cls.participants:
            if p.authenticated and p.username == username:
                print('[WebSocket] Forwarding message to', username)
                p.write_message(payload)


if __name__ == "__main__":
    PORT = 64000
    LOCAL_OUTPUT = 'ipc:///tmp/message_flow_out'

    import zmq

    # https://zeromq.github.io/pyzmq/eventloop.html
    from zmq.eventloop import ioloop, zmqstream
    ioloop.install()

    sub = ctx.socket(zmq.SUB)
    sub.connect(LOCAL_OUTPUT)
    sub.setsockopt(zmq.SUBSCRIBE, b'')

    print('[websocket_server] Broadcasting {} to all websockets'.format(LOCAL_OUTPUT))
    stream = zmqstream.ZMQStream(sub)
    stream.on_recv_stream(WebSocket.broadcast)

    server = web.Application([
        (r'/websocket', WebSocket),
    ])
    server.listen(PORT)

    # We send a heartbeat every 45 seconds to make sure that nginx
    # proxy does not time out and close the connection
    ioloop.PeriodicCallback(WebSocket.heartbeat, 45000).start()

    print('[websocket_server] Listening for incoming websocket connections on port {}'.format(PORT))
    ioloop.IOLoop.instance().start()
