class DBException(Exception):
    """
    Custom exception class for raising database exceptions
    """
    def __init__(self, message):
        super().__init__(message)
