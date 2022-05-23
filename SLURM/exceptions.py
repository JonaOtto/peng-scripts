
class SlurmBaseException(Exception):
    """
    Base exception for SLURM errors.
    """
    def __init__(self, message):
        super().__init__()
        self._message = message

    def __str__(self):
        return self._message


class ModuleDependencyConflict(SlurmBaseException):
    """
    Exception for module system modules, if there are dependency conflicts.
    """

    def __init__(self, message):
        super().__init__(message)


class ScriptNotFoundException(SlurmBaseException):
    """
    Exception for loading bash scripts, if the file could not be found.
    """

    def __init__(self, message):
        super().__init__(message)
