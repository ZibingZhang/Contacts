"""Utilities for displaying a method's progress."""
from __future__ import annotations

import functools
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def annotate(action: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def add_progress(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def with_progress(*args, **kwargs) -> T:
            starting(action)
            result = fn(*args, **kwargs)
            finished()
            return result

        return with_progress

    return add_progress


def starting(action: str) -> None:
    print(f"{action}...".ljust(50), end="", flush=True)


def message(msg: str) -> None:
    print(msg.ljust(50), end="", flush=True)


def finished() -> None:
    print("[✓]", flush=True)
