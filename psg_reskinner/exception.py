class ReskinnerException(Exception):
    def __init__(self, message):
        """
        Basic Exception class.

        First available from v2.2.0.
        :param message:
        """
        super().__init__(message)
