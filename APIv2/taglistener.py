"""
This module contains TAG related listeners
"""

from datetime import datetime
import json
import stomp

class TagListener(stomp.ConnectionListener):
    """
    A listener which waits for a response to arrive.
    """
    def __init__(self, tags):
        self.tags = tags

    def on_message(self, headers, body):
        """
        If the subscription and reply_queue can be found in the headers,
        then notify the waiting thread.
        :param dict headers: headers in the message
        :param body: the message content
        """
        if 'subscription' in headers:
            tag_id = int(headers['subscription'])
            for tag in self.tags:
                if tag['id'] == tag_id:
                    tagvalue = json.loads(body)
                    t_name = tag['name']
                    t_value = tag['value']
                    t_quality = tagvalue['quality']
                    print('%s : new value for %s: %s @ %s (%s)' % (datetime.now(),tag['name'], tagvalue['value'], tagvalue['date'] , tagvalue['quality']  ),flush=True)
