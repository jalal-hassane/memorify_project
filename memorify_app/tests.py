# Create your tests here.
import functools
import random
import string
import time
import uuid
from unittest import TestCase


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print("Finished {} in {} secs".format(repr(func.__name__), round(run_time, 3)))
        return value

    return wrapper


@timer
def doubled_and_add(num):
    res = sum([i * 2 for i in range(num)])
    print("Result : {}".format(res))


class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        """Get value of radius"""
        return self._radius

    @radius.setter
    def radius(self, value):
        """Set radius, raise error if negative"""
        if value >= 0:
            self._radius = value
        else:
            raise ValueError("Radius must be positive")

    @property
    def area(self):
        """Calculate area inside circle"""
        return self.pi() * self.radius ** 2

    def cylinder_volume(self, height):
        """Calculate volume of cylinder with circle as base"""
        return self.area * height

    @classmethod
    def unit_circle(cls):
        """Factory method creating a circle with radius 1"""
        return cls(1)

    @classmethod
    def circle_factory(cls):
        return cls(2)

    @staticmethod
    def pi():
        """Value of π, could use math.pi instead though"""
        return 3.1415926535


def repeat(*args_, **kwargs_):
    def inner_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(args_[0]):
                func(*args, **kwargs)

        return wrapper

    return inner_function


def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.num_calls += 1
        print(f"Call {wrapper.num_calls} of {func.__name__!r}")
        return func(*args, **kwargs)

    wrapper.num_calls = 0
    return wrapper


@repeat(4)
@count_calls
def say(name):
    print(f"Hello {name}")


class Tests(TestCase):

    def test_1(self):
        say("World")
        doubled_and_add(10000)
        doubled_and_add(100000)
        print(doubled_and_add.__name__)
        c = Circle(13.2)
        c.radius = 12.1
        print(c.radius)
        print(f"Hello {c.radius}")
        print("Hello world")
        print(c.area)
        c1 = Circle.unit_circle()
        c2 = Circle.circle_factory()
        print("c1 radius", c1.radius)
        print("c2 radius", c2.radius)
        print("c1 volume", c1.cylinder_volume(height=18))
        c1.radius = 16.9
        print("c1 radius after change", c1.radius)
        print("c2 radius after change", c2.radius)
        print("object1", Circle.unit_circle())
        print("object2", Circle.circle_factory())
        print("pi", Circle.pi())
        assert (1 == 1)

    def test_auth(self):
        r1 = random.randint(0, 99)
        r2 = random.randint(0, 99)
        res = (''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(20)))
        ress = "{:02d}:{:02d}:{}".format(r1, r2, res)
        print("auth", ress)
