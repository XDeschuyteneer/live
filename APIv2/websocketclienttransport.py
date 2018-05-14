"""
WebSocket transport for stomp.py.
Adapter class allowing Stomp protocol on WebSocket connection.
"""

from stomp.connect import BaseConnection, exception
from stomp.protocol import Protocol10
from stomp.transport import Transport, BaseTransport
from stomp.utils import socket

from websocket import create_connection

class WebsocketTransport(BaseTransport):
    """
    Transport over WebSocket connection.
    """
    def __init__(self, url, credentials, headers=None, auto_decode=True, wait_on_receipt=True):
        """
        This is the constructor of this object
        :param str url: the wss websocket url
        :param str credentials: the credentials
        :param dict headers: the headers to pass to the websocket
        :param bool auto_decode: decode the response as a string (default: True)
        """
        BaseTransport.__init__(self, wait_on_receipt, auto_decode)
        self.url = url
        if not headers:
            headers = {}
        headers['Authorization'] = credentials
        self.headers = headers
        self.wssocket = None
        self.vhost = ""

    def is_connected(self):
        """
        Return true if the wssocket managed by this connection is connected
        :rtype: bool
        """
        try:
            return self.wssocket is not None and BaseTransport.is_connected(self)
        except socket.error:
            return False

    def attempt_connection(self):
        """
        Establish a wssocket connection
        """
        self.wssocket = create_connection(self.url, header=self.headers)

        if not self.wssocket:
            raise exception.ConnectFailedException()

    def send(self, encoded_frame):
        """
        Send an encoded frame through the wssocket.

        :param bytes encoded_frame: the message
        """
        self.wssocket.send(encoded_frame)

    def receive(self):
        """
        Receive bytes from the wssocket.

        :rtype: bytes
        """
        receipt = self.wssocket.recv()
        return bytearray(receipt, "utf-8")

    def stop(self):
        """
        Close the websocket and stop the communication
        """
        self.running = False
        self.wssocket.close()
        BaseTransport.stop(self)


class WebsocketConnection(BaseConnection, Protocol10):
    """
    Websocket connection
    """
    def __init__(self, url, credentials, headers=None, auto_decode=True):
        """
        :param str url: the wss websocket url
        :param str credentials: the credentials
        :param dict header: the header to pass to the websocker (optional, default: None)
        :param bool auto_decode: automatically decode bytes (optional, default: True)
        """
        transport = WebsocketTransport(url, credentials, headers, auto_decode, False)
        BaseConnection.__init__(self, transport)
        Protocol10.__init__(self, transport, (0, 0))

    def connect(self, username="", passcode="", wait=True, headers=None, **keyword_headers):
        """
        :param bool wait: wait for the connection to be established
        :param dict headers: additional headers to pass to the broker
        :param keyword_headers: list of additional headers
        """

        self.transport.start()
        Protocol10.connect(
            self,
            username=username,
            passcode=passcode,
            wait=wait,
            headers=headers,
            keyword_headers=keyword_headers)

    def disconnect(self, receipt=None, headers=None, **keyword_headers):
        """
        :param str receipt:
        :param dict headers:
        :param keyword_headers:
        """
        Protocol10.disconnect(self, receipt, headers, **keyword_headers)
        self.transport.stop()
