import functools
import string

from django.shortcuts import render


# Create your views here.
def validate_headers(*args_, **kwargs_):
    def inner_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            m = args_[0]
            validate(str(m['version']))
            validate(str(m['device-id']))
            validate(str(m['device-type']))

        return wrapper

    return inner_function


@validate_headers({'version': 1, 'device-id': "asdasdasd", 'device-type': "android"})
def validate(header: str) -> bool:
    return not header


def validate_auth_token(*args_, **kwargs_):
    def inner_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(args_[0]):
                func(*args, **kwargs)

        return wrapper

    return inner_function
