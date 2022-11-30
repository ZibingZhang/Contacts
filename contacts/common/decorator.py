from typing import Any, Callable, TypeVar

T = TypeVar("T", bound=Callable[..., Any])


# https://stackoverflow.com/a/4104188
def run_once(fn: T) -> T:
    """Ensures the function is only run once.

    Args:
        fn: The function to run only once.

    Returns:
        The wrapped function.
    """

    def wrapper(*args, **kwargs) -> T:
        if not wrapper.has_run:
            wrapper.has_run = True
            wrapper.run_result = fn(*args, **kwargs)
            return wrapper.run_result
        return wrapper.run_result

    wrapper.has_run = False
    return wrapper
