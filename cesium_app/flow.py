import zmq
from .json_util import to_json


class Flow(object):
    """Send messages through websocket to frontend

    """
    def __init__(self, socket_path='ipc:///tmp/message_flow_in'):
        ctx = zmq.Context()
        pub = ctx.socket(zmq.PUB)
        pub.connect(socket_path)

        self._pub = pub

    def push(self, user, action_type, payload={}):
        """Push action to specified user over websocket.

        """
        print('Pushing action {} to {}'.format(action_type, user))
        self._pub.send(b"0 " + to_json({'user': user,
                                        'action': action_type,
                                        'payload': payload}).encode('utf-8'))
