"""Errors."""


class EncodingError(RuntimeError):
    """Raised when unable to encode a dataclass field."""

    pass


class DecodingError(RuntimeError):
    """Raised when unable to decode a dataclass field."""

    pass


class CommandQuitError(RuntimeError):
    """Raised when the input is 'Q'."""

    pass


class CommandSkipError(RuntimeError):
    """Raised when the input is ''."""

    pass
