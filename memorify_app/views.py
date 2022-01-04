import functools
import json
import random
import re
import string

import phonenumbers
from django.http import HttpResponse
# Create your views here.
from mongoengine import QuerySet
# 69:19:tHTUESKpbhHxQsDB <<< auth token
from phonenumbers import NumberParseException, carrier
from phonenumbers.phonenumberutil import number_type

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
