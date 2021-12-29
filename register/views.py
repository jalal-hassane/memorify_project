import uuid
from datetime import datetime

# Create your views here.
# needed fields in registration
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from memorify_app.models import Profile, User
from memorify_app.views import *


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


# firebase verification
def verify_code(code) -> bool:
    return True


def create_new_profile(body):
    original_phone = body.get(PHONE)
    country_code = body.get(COUNTRY_CODE)
    if not verify_code(body.get(VERIFICATION_CODE)):
        return response_fail(invalid_verification_code)
    password = body.get(PASSWORD)
    if password != body.get(VERIFY_PASSWORD):
        return response_fail(password_mismatch)
    if body.get(IS_ROOTED) == 'True':
        return response_fail(rooted_device_not_allowed)
    if body.get(IS_EMULATOR) == 'True':
        return response_fail(emulator_device_not_allowed)
    auth_token = generate_auth_token()
    profile = Profile()
    profile.auth_token = auth_token
    profile.public_id = str(uuid.uuid4())
    profile.full_name = body.get(NAME)
    profile.original_phone = original_phone
    verified_phone_number = check_valid_phone(original_phone, country_code)
    if not verified_phone_number:
        return verified_phone_number
    else:
        pass
    profile.phone = '+' + str(verified_phone_number.country_code) + str(verified_phone_number.national_number)
    profile.number_verified = True
    profile.country = get_country(country_code)
    profile.password = password
    profile.registration_ts = datetime.now()
    profile.language = body.get(LANGUAGE)
    profile.is_active = True
    profile.last_access_ts = datetime.now()
    # todo if not empty verify email through firebase
    profile.email = body.get(EMAIL)
    profile.facebook_connected = False
    profile.allowed_messages = 3
    profile.save()
    pass


def update_device(device_id, body, app_version, auth_token):
    old: QuerySet = Device.objects.filter(device_id=device_id)
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
        device.language = body.get(LANGUAGE)
        device.app_version = app_version
        device.is_rooted = bool(body.get(IS_ROOTED))
        device.is_emulator = bool(body.get(IS_EMULATOR))
        device.save()


@csrf_exempt  # bypass validation for now
@validate_headers()
@validate_body_fields(registration_body_fields)
@require_POST
# @csrf_protect
def register(request):
    body = request.POST
    print("BODY JSON1", str(request.build_absolute_uri()))
    print("BODY JSON DUMPS", json.dumps(body))
    original_phone = body.get(PHONE)
    # check for old profile
    country_code = body.get(COUNTRY_CODE)
    old_profile = Profile.objects.filter(original_phone=original_phone)
    if old_profile:
        profile = old_profile.first()
        profile.country = get_country(country_code)
    else:
        profile = create_new_profile(body)
        if isinstance(profile, HttpResponse):
            return profile
        else:
            pass

    # save device
    update_device(
        request.headers.get(HEADER_DEVICE_ID),
        body,
        request.headers.get(HEADER_APP_VERSION),
        profile.auth_token
    )

    # generate new auth token
    user = User()
    user.profile = profile
    user.auth_token = profile.auth_token
    return response_ok(user.to_json())


def register_facebook(request):
    pass


@csrf_exempt  # bypass validation for now
@validate_headers()
@validate_body_fields(login_body_fields)
@require_POST
def login(request):
    body = request.POST
    username = body.get(EMAIL_PHONE)
    password = body.get(PASSWORD)
    code = body.get(COUNTRY_CODE)
    if str(username).__contains__("@"):
        if not check_valid_email(username):
            return response_fail(invalid_email)
        else:
            # check if email exists
            profile = Profile.email_filter(username, password)
            if profile:
                profile.country = get_country(iso_2_country_code=code)
            else:
                return response_fail(wrong_credentials)
    else:
        # phone number
        profile = Profile.phone_filter(username, password)
        if profile:
            profile.country = get_country(iso_2_country_code=code)
        else:
            return response_fail(wrong_credentials)

    auth_token = generate_auth_token()
    update_device(
        request.headers.get(HEADER_DEVICE_ID),
        body,
        request.headers.get(HEADER_APP_VERSION),
        auth_token
    )
    profile.auth_token = auth_token
    profile.save()
    login_response = {
        AUTH_TOKEN: auth_token,
        PROFILE: profile.to_json()
    }
    return response_ok(login_response)


def request_code(request):
    pass


def update_phone(request):
    pass
