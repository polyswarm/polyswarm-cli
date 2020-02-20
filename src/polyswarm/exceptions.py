class PolyswarmException(Exception):
    pass


#########################################
# Search Exceptions
#########################################

class NoResultsException(PolyswarmException):
    pass


class NotFoundException(PolyswarmException):
    pass


class InternalFailureException(PolyswarmException):
    pass


class PartialResultsException(PolyswarmException):
    pass
