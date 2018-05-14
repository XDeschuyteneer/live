import stomp

class DebugMessageListener(stomp.ConnectionListener):
    """
    A listener which just print received messages body and their headers
    Use it as debug purpose.
    Register it like this: ws_connection.set_listener('debug', DebugMessageListener())
    """
    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        print('received a message for "%s"' % headers)
        print('message body "%s"' % message)
