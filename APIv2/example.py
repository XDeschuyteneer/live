"""
This program is a test for datasnapshot T2M API
"""
import argparse
import os
import logging
import pprint
import datetime
from functools import partial
from websocket._exceptions import WebSocketBadStatusException
from time import sleep

from APIv2 import credentials
from APIv2.requestreplyhandler import RequestReplyHandler
from APIv2.taglistener import TagListener
from APIv2.websocketclienttransport import WebsocketConnection

class Example(object):
    """
    This small application will connect to data.talk2m.com using Stomp Over Websocket.
    """

    SUBSCRIPTION_ID = 1
    REPLY_QUEUE_NAME = '/user/queue/replies'
    DATASNAPSHOT_BASE_URI = 'wss://data.talk2m.com/v2/ws/websocket'

    def __init__(self, cred_file_name):
        """
        Constructor of the Example class
        :param str cred_file_name: the path to the credential file
        """
        print ("%s : Connecting to %s..." % (datetime.datetime.now(),
            'wss://data.talk2m.com/v2/ws/websocket'))
        self.ws_connection = WebsocketConnection(
            Example.DATASNAPSHOT_BASE_URI,
            credentials.encode_from_file(cred_file_name))

        #Request-reply handler will be responsible to listen for replies
        self.request_reply_handler = RequestReplyHandler(
            Example.SUBSCRIPTION_ID,
            Example.REPLY_QUEUE_NAME)
        self.ws_connection.set_listener('request', self.request_reply_handler)

        #start and connect API with stomp
        self.ws_connection.start()
        try:
            self.ws_connection.connect(wait=True)
        except WebSocketBadStatusException as wsbse:
            print("Cannot Connect: %s, please verify your credentials" % wsbse)
            quit()

        #Subscribe to reply queue to get response of each /GET/ commands sent
        logging.info ("Connected, will subscribe to reply queue..." )
        self.ws_connection.subscribe(
            destination=Example.REPLY_QUEUE_NAME,
            id=Example.SUBSCRIPTION_ID,
            ack='auto')

    def get_account(self):
        """
        This method retrieves basic account information as well as
        the set of pools visible by user and the name of each custom attribute.
        :param str ewon_name: the ewon name (as registered in T2M account)
        """
        #response to /GET/ will arrive in REPLY_QUEUE_NAME
        print ("%s : /GET/account..." % (datetime.datetime.now()))
        self.ws_connection.send(destination='/GET/account', body='{}')
        #Wait until the response arrive
        response = self.request_reply_handler.wait_on_response()
        try:
            pprint.pprint(response)
        except Exception as exc:
            print(exc)
            quit()


    def subscribe_all_ewon_tag(self, ewon_name, get_tag_values_first):
        """
        This method subscribe to all TAGs of an eWON
        :param str ewon_name: the ewon name (as registered in T2M account)
        :param bool get_tag_values_first : use /GET/tag/%s/value to get tag values
        """
        #response to /GET/ will arrive in REPLY_QUEUE_NAME
        print ("%s : /GET/ewons..." % (datetime.datetime.now()))
        self.ws_connection.send(destination='/GET/ewons', body='{}')
        #Wait until the response arrive
        response = self.request_reply_handler.wait_on_response()
        try:
            my_ewon = Example.find_ewon(response, ewon_name)
            e_status = my_ewon["status"]
            e_name = my_ewon["name"]
            e_id = my_ewon["id"]
            print('%s : found %s ewon %s with id %d ' % (datetime.datetime.now(),
                e_status, e_name, e_id))

            if e_status != "online":
                print("eWON %s must be online!" % e_name)
                quit()

            print ("%s : /GET/ewon/%d/tags" % (datetime.datetime.now(),e_id))
            tags_command = "/GET/ewon/%d/tags" %  e_id
            self.ws_connection.send(destination=tags_command, body='{}')
            #Wait until the response arrive
            response = self.request_reply_handler.wait_on_response()

            tags = response["tags"]
            #Create the message listener and register it to the connection.
            tag_listener = TagListener(tags)
            self.ws_connection.set_listener('tags', tag_listener)

            #demonstrate fetching tag value
            if get_tag_values_first:
                for tag in tags:
                    tagval_command = "/GET/tag/%s/value" %  tag['id']
                    print("%s : %s (%s) ... " % (datetime.datetime.now(),tagval_command,tag["name"]),
                        end='')
                    self.ws_connection.send(destination=tagval_command, body='{}')
                    response = self.request_reply_handler.wait_on_response()
                    print(" : %s" %  response["value"])

            for tag in tags:
                subscription = "/exchange/ewons/%d.tags.%d.value" % (e_id, tag['id'])
                print('%s : subscribing to %s' % (datetime.datetime.now(),tag['name']) )
                self.ws_connection.subscribe(destination=subscription, id=tag['id'], ack='auto')

        except Exception as exc:
            print(exc)
            quit()

    def disconnect(self):
        """
        This method disconnects the websocket
        """
        self.ws_connection.disconnect()

    @staticmethod
    def find_ewon(response, ewon_name):
        """
        This method find an ewon in the datasnapshot response
        :param dict response: the datasnapshot JSON response
        :param str ewon_name: the name of the eWON to search
        """
        rjson = response["ewons"]
        ewons = ""
        for ewon in rjson:
            if ewon["name"] == ewon_name:
                return ewon
            else:
                ewons = "{0}'{1}'{2}".format(ewons, ewon["name"], os.linesep)
        raise NameError("ewon not found in ewons list:{0}{1}".format(os.linesep, ewons))


def main(ewon_name, credentials_file, log_level, get_account):
    """
    This is the main function to run
    :param str ewon_name: the name of your eWON
    :param str credentials_file: the path of your credential file
    :param bool get_account: run /get/account ?
    :Example:
    >>> main('myflexy', './myT2Mcredentials', 'WARN', True)
    """

    #Change INFO to DEBUG if needed
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')

    example = Example(credentials_file)

    try:
        if get_account:
            logging.info("Will launch get_account...")
            example.get_account()


        logging.info("Will launch subscribe_all_ewon_tag...")
        example.subscribe_all_ewon_tag(ewon_name, True)
        print("Press CTRL+C to stop...")
        while True:
           sleep(60)
    except KeyboardInterrupt:
        pass
    print("Disconnecting...")
    example.disconnect()

def launch():
    #We want unbuffered stdout, let's flush every print
    global print
    print = partial(print, flush=True)

    PARSER = argparse.ArgumentParser(description='T2M Live Data example program')
    PARSER.add_argument(
        'ewon_name',
        metavar='EWON_NAME',
        type=str,
        help='your eWON name registered in your T2M account')
    PARSER.add_argument(
        "-c",
        metavar='CREDENTIALS_FILE',
        type=str,
        nargs='?',
        default="credentials",
        help='your credential file')
    PARSER.add_argument(
        "-d",
        metavar='LOG_LEVEL',
        type=str,
        nargs='?',
        default="WARN",
        const="DEBUG",
        help='Activate debug mode & specify your loglevel (WARN,INFO)')
    PARSER.add_argument(
        "-a",
        action='store_true',
        help='Get account information')    
    ARGS = PARSER.parse_args()
    main(ARGS.ewon_name, ARGS.c, ARGS.d, ARGS.a)

if __name__ == '__main__':
    launch()

