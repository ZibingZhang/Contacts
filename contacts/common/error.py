class EncodingError(RuntimeError):
    """Raised when unable to encode a dataclass field."""


class DecodingError(RuntimeError):
    """Raised when unable to decode a dataclass field."""


class CommandQuitError(RuntimeError):
    """Raised when the input is 'Q'."""


class CommandSkipError(RuntimeError):
    """Raised when the input is ''."""
