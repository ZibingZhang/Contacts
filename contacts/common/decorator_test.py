from common.decorator import run_once

times_run = 0


@run_once
def example_function():
    global times_run
    times_run += 1


def test_decorator_run_once():
    global times_run
    times_run = 0

    example_function()
    example_function()

    assert times_run == 1
