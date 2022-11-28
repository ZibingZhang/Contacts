from common.singleton import Singleton


class Class(metaclass=Singleton):
    pass


def test_singleton():
    obj_1 = Class()
    obj_2 = Class()
    assert obj_1 is obj_2
