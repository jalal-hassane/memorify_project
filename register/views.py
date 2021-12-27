import functools
import uuid
from datetime import datetime
from uuid import UUID

from django.http import HttpResponse
from django.shortcuts import render
import json
from urllib.parse import urlparse
# Create your views here.
# needed fields in registration
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from mongoengine import QuerySet

from memorify_app.models import Profile, Device, User, Country
from memorify_app.views import validate_headers, response_fail, response_ok, validate_body_fields, generate_auth_token

import phonenumbers

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
registration_body_fields = [
    "name",
    "phone",
    "password",
    "verify_password",
    "user_timezone",
    "user_timezone_region",
    "language",
    "device_name",
    "device_os_version",
    "device_oem",
    "mobile_carrier",
    "app_store_version",
    "is_rooted",
    "is_emulator",
    "country_code",
    "verification_code",
]


def get_calling_code(iso):
    for code, isos in phonenumbers.COUNTRY_CODE_TO_REGION_CODE.items():
        if iso.upper() in isos:
            return code
    return None


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


def verify_code(code) -> bool:
    return True


def get_profile_country(iso_2_country_code):
    country = Country.objects.filter(iso_2=iso_2_country_code)
    if country:
        return country.first().to_json()
    else:
        return {}


@csrf_exempt  # bypass validation for now
@validate_headers()
@validate_body_fields(registration_body_fields)
@require_POST
# @csrf_protect
def register(request):
    body = request.POST
    original_phone = body.get(PHONE)
    # check for old profile
    country_code = body.get(COUNTRY_CODE)
    old_profile = Profile.objects.filter(original_phone=original_phone)
    if old_profile:
        profile = old_profile.first()
        profile.country = get_profile_country(country_code)
    else:
        profile = Profile()
        profile.public_id = str(uuid.uuid4())
        profile.full_name = body.get(NAME)
        profile.original_phone = original_phone
        obj = phonenumbers.parse('+' + str(get_calling_code(country_code)) + profile.original_phone)
        if not phonenumbers.is_possible_number(obj):
            return response_fail("Phone number is not valid")
        profile.phone = '+' + str(obj.country_code) + str(obj.national_number)
        profile.number_verified = True
        profile.country = get_profile_country(country_code)
        profile.password = body.get(PASSWORD)
        if profile.password != body.get(VERIFY_PASSWORD):
            return response_fail("Password does not match")
        if body.get(IS_ROOTED) == 'True':
            return response_fail("Rooted devices are not allowed to enter the app")
        if body.get(IS_EMULATOR) == 'True':
            return response_fail('Emulators are not allowed to enter the app')
        if not verify_code(body.get(VERIFICATION_CODE)):
            return response_fail("Verification code is not correct")
        profile.registration_ts = datetime.now()
        profile.language = body.get(LANGUAGE)
        profile.is_active = True
        profile.last_access_ts = datetime.now()
        # todo if not empty verify email through firebase
        profile.email = body.get("email")
        profile.facebook_connected = False
        profile.allowed_messages = 3
        profile.save()
    #  todo save device
    auth_token = generate_auth_token()
    old: QuerySet = Device.objects.filter(device_id=request.headers.get('device-id'))
    if old:
        device = old.first()
        device.auth_token = auth_token
        device.timezone = body.get(TIMEZONE)
        device.timezone_region = body.get(TIMEZONE_REGION)
        device.device_token = body.get(DEVICE_TOKEN)
        device.model = body.get(DEVICE_NAME)
        device.os_version = body.get(DEVICE_OS_VERSION)
        device.manufacturer = body.get(DEVICE_OEM)
        device.operator = body.get(MOBILE_CARRIER)
        device.app_store_version = body.get(APP_STORE_VERSION)
        device.app_version = request.headers.get('app-version')
        device.is_rooted = bool(body.get(IS_ROOTED))
        device.is_emulator = bool(body.get(IS_EMULATOR))
        device.language = body.get(LANGUAGE)
        device.save()

    # todo return httpResponse
    # generate new auth token
    user = User()
    user.profile = profile
    user.auth_token = auth_token
    return response_ok(user)


def register_facebook(request):
    pass


def login(request):
    pass


def request_code(request):
    pass


def update_phone(request):
    pass
