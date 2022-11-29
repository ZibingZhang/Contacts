from typing import Any, Callable


def annotate(action: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrap(fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped_fn(*args, **kwargs) -> Any:
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
