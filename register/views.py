import functools

from django.http import HttpResponse
from django.shortcuts import render
import json
from urllib.parse import urlparse
# Create your views here.
# needed fields in registration
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from memorify_app.models import Profile
from memorify_app.views import validate_headers, response_fail, response_ok, validate_body_fields, validate_auth_token

NAME = "name"
PHONE = "phone"
PASSWORD = "password"
VERIFY_PASSWORD = "verify_password"
TIMEZONE = "user_timezone"
TIMEZONE_REGION = "user_timezone_region"
LANGUAGE = "language"
DEVICE_TOKEN = "device_token"
DEVICE_NAME = "device_name"
DEVICE_OS_VERSION = "device_os_version"
DEVICE_OEM = "device_oem"
MOBILE_CARRIER = "mobile_carrier"
APP_STORE_VERSION = "app_store_version"
IS_ROOTED = "is_rooted"
IS_EMULATOR = "is_emulator"
COUNTRY_CODE = "country_code"
VERIFICATION_CODE = "verification_code"


# RegisterRequest
class RegisterRequest:
    name: str = ""
    phone: str = ""
    password: str = ""
    verify_password: str = ""
    timezone: str = ""
    timezone_region: str = ""
    language: str = ""
    device_token: str = ""
    device_name: str = ""
    device_os_version: str = ""
    device_oem: str = ""
    device_carrier: str = ""
    app_store_version: str = ""
    is_rooted: bool = False
    is_emulator: bool = False
    country_code: str = ""
    verification_code: str = ""
    pass


class RegisterResponse:
    auth_token: str = ""
    profile = Profile()
    is_new_user: bool = True

    def to_json(self):
        return {
            "auth_token": self.auth_token,
            "profile": self.profile.to_json(),
            "is_new_user": self.is_new_user
        }


class TestBody:
    test_key: str = ""
    key_2: str = ""
    key_3: str = ""

    def verify_attribute(self, param):
        if not param:
            return False
        return param

    def __init__(self, body):
        self.test_key = body.get('test_key')
        self.key_2 = body.get('key_2')
        self.key_3 = body.get('key_3')

    @classmethod
    def to_test_body(cls, body):
        return cls(body)


@csrf_exempt  # bypass validation for now
@validate_auth_token
@validate_body_fields(['test_key', 'key_2', 'key_3'])
@require_POST
# @csrf_protect
def register(request):
    print("REQUEST", request)
    print("HEADERS", request.headers)
    # fetching request body fields
    body = request.POST
    print("body", body)
    print("body keys", body.keys())
    print("body values", body.values())
    tbody = TestBody.to_test_body(body)
    print("TestBody1", tbody.test_key)
    print("TestBody2", tbody.key_2)
    print("TestBody3", tbody.key_3)
    print("test_key", body.get('test_key'))
    return response_ok({})


def register_facebook(request):
    pass


def login(request):
    pass


def request_code(request):
    pass


def update_phone(request):
    pass
