"""A password filter."""

from __future__ import annotations

import logging


class PasswordFilter(logging.Filter):
    """Hides the password when logging."""

    def __init__(self, password: str) -> None:
        super().__init__(password)

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        if self.name in message:
            record.msg = message.replace(self.name, "*" * 8)
            record.args = ()
        return True
