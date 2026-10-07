class DomainError(Exception):
    """Base for errors the HTTP layer maps to a status code."""


class NotFound(DomainError):
    pass


class ValidationFailed(DomainError):
    pass
