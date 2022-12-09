"""Tests for contacts.common.decorator."""
from __future__ import annotations

from contacts.common import decorator

times_run = 0


@decorator.run_once
def example_function() -> None:
    global times_run
    times_run += 1


def test_decorator_run_once() -> None:
    global times_run
    times_run = 0

    example_function()
    example_function()

    assert times_run == 1
