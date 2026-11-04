"""Business-rule errors. main.py turns them into HTTP responses."""


class NotFoundError(Exception):
    """The requested record does not exist (HTTP 404)."""


class ConflictError(Exception):
    """The request clashes with existing data, e.g. a duplicate name (HTTP 409)."""
