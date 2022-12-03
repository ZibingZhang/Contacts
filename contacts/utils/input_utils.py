"""Utilities for getting user input."""
from common import error


def basic_input(
    prompt: str, lower: bool = False, options: tuple[str, ...] | None = ()
) -> str:
    options = (options or ()) + ("Q",)
    response = input(f"{prompt} [{'/'.join(options)}]: ").strip()
    if response.lower() == "q":
        raise error.CommandQuitError
    if lower:
        response = response.lower()
    return response


def yes_no_input(prompt: str) -> bool:
    return basic_input(prompt, lower=True, options=("Y", "N")) == "y"


def input_with_skip(
    prompt: str, lower: bool = False, options: tuple[str] | None = ()
) -> str:
    response = basic_input(prompt, lower, options)
    if not response:
        raise error.CommandSkipError
    return response
