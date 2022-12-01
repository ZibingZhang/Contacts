from typing import Callable, TypeVar

T = TypeVar("T")


def annotate(action: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def wrap(fn: Callable[..., T]) -> Callable[..., T]:
        def wrapped_fn(*args, **kwargs) -> T:
            starting(action)
            result = fn(*args, **kwargs)
            finished()
            return result

        return wrapped_fn

    return wrap


def starting(action: str) -> None:
    print(f"{action}...".ljust(46), end="\t")


def message(msg: str) -> None:
    print(msg.ljust(46), end="\t")


def finished() -> None:
    print("[✓]")
