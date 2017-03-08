import zmq
from .json_util import to_json


class Flow(object):
    """Send messages through websocket to frontend

    """
    def __init__(self, socket_path='ipc:///tmp/message_flow_in'):
        self._socket_path = socket_path
        self._ctx = zmq.Context()

    def push(self, username, action_type, payload={}):
        """Push action to specified user over websocket.

        """
        pub = self._ctx.socket(zmq.PUB)
        pub.connect(self._socket_path)

        print('Pushing action {} to {}'.format(action_type, username))
        pub.send(b"0 " + to_json(
            {
                'username': username,
                'action': action_type,
                'payload': payload
            }).encode('utf-8'))

        pub.close()
