"""Exceptions used by Youfone."""


class YoufoneException(Exception):
    """Base class for all exceptions raised by Youfone."""

    pass


class YoufoneServiceException(Exception):
    """Raised when service is not available."""

    pass


class BadCredentialsException(Exception):
    """Raised when credentials are incorrect."""

    pass


class NotAuthenticatedException(Exception):
    """Raised when session is invalid."""

    pass


class GatewayTimeoutException(YoufoneServiceException):
    """Raised when server times out."""

    pass


class BadGatewayException(YoufoneServiceException):
    """Raised when server returns Bad Gateway."""

    pass
