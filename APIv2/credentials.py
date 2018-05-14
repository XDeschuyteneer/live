"""
This module contains some utility function for credentials decoding
"""

import base64

def encode_from_file(filename):
    """
    This function encode the content of the credential file for datasnapshot authentication
    :param filename: the path of the file containing the credentials
    :rtype: str
    :Example:
    >>> encode_from_file("./mycredentials")
    """
    with open(filename) as file:
        credential = file.read()
        b64 = base64.b64encode(credential.encode())
        return "Talk2M " + b64.decode("utf-8", "strict")
    file.close()
