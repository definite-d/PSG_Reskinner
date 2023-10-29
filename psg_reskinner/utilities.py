from functools import cache


@cache
def _lower_class_name(_object):
    return type(_object).__name__.lower()


def transprint(object, **kwargs):
    print(object, **kwargs)
    return object


def clamp(v: float):
    return min(max(v, 0), 1)
