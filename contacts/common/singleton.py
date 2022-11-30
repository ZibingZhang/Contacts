# https://stackoverflow.com/a/6798042
class Singleton(type):
    """Ensures the class is only instantiated once."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
