import functools
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

    @functools.wraps(fn)
    def with_cached_result(*args, **kwargs) -> T:
        if not with_cached_result.has_run:
            with_cached_result.has_run = True
            with_cached_result.run_result = fn(*args, **kwargs)
            return with_cached_result.run_result
        return with_cached_result.run_result

    with_cached_result.has_run = False
    return with_cached_result
