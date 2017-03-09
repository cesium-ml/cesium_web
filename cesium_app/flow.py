import zmq
from .json_util import to_json


class Flow(object):
    """Send messages through websocket to frontend

    """
    def __init__(self, socket_path='ipc:///tmp/message_flow_in'):
        self._socket_path = socket_path
        self._ctx = zmq.Context.instance()
        self._pub = self._ctx.socket(zmq.PUB)
        self._pub.connect(self._socket_path)

    def push(self, username, action_type, payload={}):
        """Push action to specified user over websocket.

        """
        print('Pushing action {} to {}'.format(action_type, username))
        message = [username,
                   to_json({'username': username,
                            'action': action_type,
                            'payload': payload})]
        self._pub.send_multipart([m.encode('utf-8') for m in message])
