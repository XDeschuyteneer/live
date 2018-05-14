"""
This module contains some handlers for the datasnapshot messages
"""

import stomp
import threading
import json
from APIv2.apierror import APIError

class RequestReplyHandler(stomp.ConnectionListener):
    """
    A listener which waits for a response to arrive.
    """
    def __init__(self, subscription, reply_queue):
        """
        This is the constructor of the class
        :param str subscription: the topic to subscribe
        :param str reply_queue: the reply queue
        """

        self.condition = threading.Condition()
        self.reply_queue = reply_queue
        self.subscription = subscription
        self.received = False
        self.response = ""

    def on_message(self, headers, body):
        """
        If the subscription and reply_queue can be found in the headers,
        then notify the waiting thread.
        :param dict headers: headers in the message
        :param str body: the message content
        """
        if (
                'subscription' in headers and
                int(headers['subscription']) == self.subscription and
                'destination' in headers and
                headers['destination'] == self.reply_queue
            ):
            with self.condition:
                self.received = True
                self.response = body
                self.condition.notify()

    def wait_on_response(self):
        """
        Wait until we receive a message receipt.
        """
        with self.condition:
            while not self.received:
                self.condition.wait()
        self.received = False
        rjson = json.loads(self.response)
        if rjson["success"] is False:
            raise APIError(rjson["code"], rjson["message"])
        return rjson
