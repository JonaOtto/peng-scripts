

class AnalyzerBaseException(Exception):
    """
    Base exception for SLURM errors.
    """
    def __init__(self, message):
        super().__init__()
        self._message = message

    def __str__(self):
        return self._message


class NamingSchemeException(AnalyzerBaseException):
    """
    Exception for naming scheme errors.
    """
    def __init__(self, message):
        super(NamingSchemeException, self).__init__(message)
