""""
This module contains T2M datasnapshot error class
"""

class APIError(Exception):
    """
    This class represents a generic T2M datasnapshot error
    """
    def __init__(self, code, message):
        """
        Constructor of this error
        :param int code: the error code
        :param str message: the error message
        """
        super(APIError, self).__init__(message)
        self.code = code
        self.message = message

    def __str__(self):
        return repr('API Error code %d: %s' %(self.code, self.message))