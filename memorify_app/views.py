import functools
import json
import random
import string

from bson import ObjectId
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from mongoengine import QuerySet

from memorify_app.models import Device

# 69:19:tHTUESKpbhHxQsDB <<< auth token
# todo add constants file in which we add request/response params
version_required = "Missing version in headers"
device_id_required = "Missing device-id in headers"
device_not_exist = "Device does not exist"
device_type_required = "Missing device-type in headers"
auth_token_required = "Missing auth-token in headers"
auth_token_not_valid = "auth-token is not valid"
country_code_required = "country_code field must not be empty"
country_code_not_available = "country_code field is not available"


def response_ok(j_obj):
    if not j_obj:
        payload = {}
    else:
        payload = j_obj.to_json()
    response = {
        "status": "SUCCESS",
        "payload": payload
    }
    return HttpResponse(json.dumps(response), content_type="application/json")


def response_fail(error):
    response = {
        "status": "FAIL",
        "message": error,
        "dev_message": "dev message"
    }
    return HttpResponse(json.dumps(response), content_type="application/json")


def generate_auth_token(self):
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
            m_headers = ['app-version', 'device-id', 'device-type']
            if kwargs_:
                for arg in kwargs_['kwargs_']:
                    m_headers.append(arg)
            print("ARGS", args)
            print("M_HEADERS", m_headers)
            headers = args[0].headers
            print("HEADERS12", headers)
            if not headers:
                return response_fail('Headers fields are all missing')
            for h in m_headers:
                if h not in headers.keys() or not headers.get(h):
                    return response_fail('Missing fields: ' + h)
            auth = headers.get('auth-token')
            d_id = headers.get('device-id')
            if validate_auth_token(auth, d_id):
                return response_fail(validate_auth_token(auth, d_id))
            old: QuerySet = Device.objects.filter(device_id=d_id)
            print("Old device", old)
            if old:
                device = old.first()
                old.app_version = headers.get('app-version')
            else:
                device = Device(
                    device_id=d_id,
                    type=headers.get('device-type'),
                    app_version=headers.get('app-version')
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
            if not body:
                return response_fail('Body fields are all missing')
            for k in args_[0]:
                if not body.get(k):
                    return response_fail('Missing fields: ' + k)
            return func(*args)

        return wrapper

    return inner_function
