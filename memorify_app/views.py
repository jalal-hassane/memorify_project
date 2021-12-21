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


def validate_headers(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        m_headers = ['app-version', 'device-id', 'device-type']
        print("ARGS",args)
        headers = {}
        print("HEADERS12", headers)
        has_empty_fields = False
        if not headers:
            return response_fail('Headers fields are all missing')
        for h in m_headers:
            if h not in headers.keys():
                return response_fail('Missing fields: ' + h)
        print("has empty fields", has_empty_fields)
        if not has_empty_fields:
            old: QuerySet = Device.objects.filter(device_id=headers.get('device-id'))
            print("Old device", old)
            if old:
                device = old.first()
                old.app_version = headers.get('version')
            else:
                device = Device(
                    device_id=headers.get('device-id'),
                    type=headers.get('device-type'),
                    app_version=headers.get('version')
                )
            print("DEVICE", device)
            device.save()
            return func(*args)
        else:
            return response_fail("Error")

    return wrapper


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


# validate existing auth token, otherwise assign the auth token to the existing device
# todo validate headers
# @validate_headers
def validate_auth_token(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        headers = args[0].headers
        print("HHH", headers)
        auth = headers.get("auth-token")
        if not auth:
            return response_fail(auth_token_required)
        old: QuerySet = Device.objects.filter(device_id=headers.get('device-id'))
        if old:
            device = old.first()
            if not device.auth_token:
                device.auth_token = auth
                device.save()
                return func(*args)
            else:
                # device has an auth token, checking for match
                if device.auth_token != auth:
                    return response_fail(auth_token_not_valid)
                else:
                    # all good, return None for proceeding with api
                    return func(*args)
        else:
            return response_fail(device_not_exist)

    return wrapper
