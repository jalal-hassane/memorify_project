import functools
from unittest import TestCase

from django.test import TestCase


def validate_headers(*args_, **kwargs_):
    def inner_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            m = args_[0]
            print(m['version'])
            print(m['device-id'])
            print(m['device-type'])
            func(*args)

        return wrapper

    return inner_function


@validate_headers(['version', 'device-id', 'device-type'])
def validate(header: dict) -> bool:
    print(header)
    return True


# Create your tests here.
class Test(TestCase):
    def test_validate(self):
        validate({'version': 1, 'device-id': "asdasdasd", 'device-type': "android"})
