from common.singleton import Singleton


class Class(metaclass=Singleton):
    pass


def test_singleton_class_objects_are_the_same():
    obj_1 = Class()
    obj_2 = Class()
    assert obj_1 is obj_2
