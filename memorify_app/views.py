import functools
import json
import random
import re
import string

import phonenumbers
import requests
from django.http import HttpResponse
# Create your views here.
from mongoengine import QuerySet
# 69:19:tHTUESKpbhHxQsDB <<< auth token
from phonenumbers import NumberParseException, carrier
from phonenumbers.phonenumberutil import number_type
from pyfcm import FCMNotification

from memorify_app.constants import *
from memorify_app.models import Device, Country


def response_ok(payload):
    response = {
        STATUS: SUCCESS,
        MESSAGE: SUCCESS,
        PAYLOAD: payload
    }
    return HttpResponse(json.dumps(response), content_type=CONTENT_TYPE_JSON)


def response_fail(error):
    response = {
        STATUS: SUCCESS,
        MESSAGE: FAIL,
        DEV_MESSAGE: error
    }
    return HttpResponse(json.dumps(response), content_type=CONTENT_TYPE_JSON)


def generate_auth_token():
    r1 = random.randint(0, 99)
    r2 = random.randint(0, 99)
    r3 = (''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(20)))
    auth = "{:02d}:{:02d}:{}".format(r1, r2, r3)
    print("auth", auth)
    return auth


# validate existing auth token, otherwise assign the auth token to the existing device
def validate_auth_token(auth, device_id):
    print("AUTH to validate", auth)
    print("Device to validate", device_id)
    old: QuerySet = Device.objects.filter(device_id=device_id)
    if old:
        print("OLD:::", old)
        device = old.first()
        if not device.auth_token:
            print("not device.auth_token:::", device.auth_token)
            device.auth_token = auth
            device.save()
            return None
        else:
            # device has an auth token, checking for match
            print("device.auth_token:::", device.auth_token)
            if device.auth_token != auth:
                print("device.auth_token != auth:::", device.auth_token)
                return auth_token_not_valid
            else:
                return None
    else:
        return device_not_exist


def validate_headers(*args_, **kwargs_):
    def inner_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            m_headers = [HEADER_APP_VERSION, HEADER_DEVICE_ID, HEADER_DEVICE_TYPE]
            if kwargs_:
                for arg in kwargs_['kwargs_']:
                    m_headers.append(arg)
            print("ARGS", args)
            print("M_HEADERS", m_headers)
            headers = args[0].headers
            print("HEADERS12", headers)
            if not headers:
                return response_fail(headers_fields_required)
            for h in m_headers:
                if h not in headers.keys() or not headers.get(h):
                    return response_fail(f'{missing_headers_fields}{h}')

            d_id = headers.get(HEADER_DEVICE_ID)
            if HEADER_AUTH_TOKEN in headers.keys():
                auth = headers.get(HEADER_AUTH_TOKEN)
                if validate_auth_token(auth, d_id):
                    return response_fail(validate_auth_token(auth, d_id))
            old: QuerySet = Device.objects.filter(device_id=d_id)
            print("Old device", old)
            if old:
                device = old.first()
                old.app_version = headers.get(HEADER_APP_VERSION)
            else:
                device = Device(
                    device_id=d_id,
                    type=headers.get(HEADER_DEVICE_TYPE),
                    app_version=headers.get(HEADER_APP_VERSION)
                )
            print("DEVICE", device)
            device.save()
            return func(*args)

        return wrapper

    return inner_function


def validate_body_fields(*args_, **kwargs_):
    def inner_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            body = args[0].POST
            print("BODY FIELDS", body)
            if not body:
                return response_fail(body_fields_required)
            for k in args_[0]:
                if not body.get(k):
                    return response_fail(f'{missing_body_fields}{k}')
            return func(*args)

        return wrapper

    return inner_function


def get_country(iso_2_country_code, iso_3: str = ""):
    if iso_3:
        country = Country.objects.filter(code=iso_3.upper())
    else:
        country = Country.objects.filter(iso_2=iso_2_country_code.upper())
    if country:
        return country.first().to_json()
    else:
        return {}


# use iso2 code
def get_calling_code(iso):
    for code, isos in phonenumbers.COUNTRY_CODE_TO_REGION_CODE.items():
        if iso.upper() in isos:
            return code
    return None


def check_valid_phone(phone, country_code):
    if not country_code:
        international_number = phone
    else:
        international_number = '+' + str(get_calling_code(country_code)) + phone
    # todo try catch
    try:
        print("INTERNATIONAL", international_number)
        obj = phonenumbers.parse(international_number)
        is_mobile = carrier._is_mobile(number_type(obj))
        if is_mobile:
            print("OBJECT", obj)
            phonenumbers.is_valid_number(obj)
            print("is valid", "Valid")
            international_number = '+' + str(obj.country_code) + str(obj.national_number)
            return international_number
        else:
            return response_fail(invalid_phone_number)
    except NumberParseException:
        print("INTERNATIONAL2", international_number)
        return response_fail(invalid_phone_number)
    finally:
        pass


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def check_valid_email(email):
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def update_device(device_id, body, app_version, auth_token):
    device = Device.device_id_filter(device_id)
    if not device:
        return
    device.auth_token = auth_token
    device.app_version = app_version
    tz = body[TIMEZONE]
    if tz:
        device.timezone = tz

    tz_region = body[TIMEZONE_REGION]
    if tz_region:
        device.timezone_region = tz_region

    token = body[DEVICE_TOKEN]
    if token:
        device.device_token = token

    model = body[DEVICE_NAME]
    if model:
        device.model = model

    os_version = body[DEVICE_OS_VERSION]
    if os_version:
        device.os_version = os_version

    device_oem = body[DEVICE_OEM]
    if device_oem:
        device.manufacturer = device_oem

    mobile_carrier = body[MOBILE_CARRIER]
    if mobile_carrier:
        device.operator = mobile_carrier

    app_store_version = body[APP_STORE_VERSION]
    if app_store_version:
        device.app_store_version = app_store_version

    language = body[LANGUAGE]
    if language:
        device.language = language

    is_rooted = body[IS_ROOTED]
    if is_rooted:
        device.is_rooted = json.loads(is_rooted)

    is_emulator = body[IS_EMULATOR]
    if is_emulator:
        device.is_emulator = json.loads(is_emulator)

    device.save()


# todo send message if user is not registered in the database through Twilio
def send_push(token, data):
    if token == "":
        # send message to user
        pass
    url = "https://fcm.googleapis.com/fcm/send"
    t = "c3xrdiG0TH65XRpbRBzQea:APA91bGbL7DuvbWwJj6k1nCRLFGVviPWbOisrAFLIWlq-X0LC7On-" \
        "NX5z6oYVGzB3M8f6ryh12p4BlvIiDBH27W6nZkXRWmNO3g21ZbM_ZoZdD5vjCcin_i3nS5he5GHp3HADZoF9hJ7"
    push_service = FCMNotification(api_key="AAAAH8mdaxM:APA91bGwzaNxn8nUCMQOB0qZzuaEL-JCkSmw-"
                                           "jQBphyQBrRSbE3oISaOHPWMuaYL0edKAiiO1uiv6kVR0JhSnmgFW-"
                                           "3aqtJV3RQLgb_mlKOisTmslTjvZphbTgRADGrjP78y3CavxDEr")

    registration_id = t
    message_title = "Welcome"
    message_body = "Hello, this a welcome test message"
    result = push_service.notify_single_device(registration_id=registration_id,
                                               message_title=message_title,
                                               message_body=message_body)
    print("RESULT", result)
