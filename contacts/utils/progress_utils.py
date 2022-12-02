import functools
from typing import Callable, TypeVar

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
    print(f"{action}...".ljust(46), end="\t", flush=True)


def message(msg: str) -> None:
    print(msg.ljust(46), end="\t", flush=True)


def finished() -> None:
    print("[✓]", flush=True)
