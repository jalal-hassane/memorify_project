import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from memorify_app.models import AppSettings, Profile

# Create your views here.
from memorify_app.views import *


# {country_code} needed here
@validate_headers()
def app_settings(request):
    country_code = request.GET.get(COUNTRY_CODE)
    if not country_code:
        return response_fail(country_code_required)
    print("Country code", country_code)
    settings = AppSettings.country_filter(country_code)
    print("Settings", settings)
    if not settings:
        return response_fail(country_code_not_available)
    return response_ok({APP_SETTINGS: settings.to_json()})


def firebase_email_verification(request):
    pass


@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(change_password_fields)
@csrf_exempt  # bypass validation for now
@require_POST
def change_password(request):
    body = request.POST
    password = body.get(PASSWORD)
    verify_password = body.get(VERIFY_PASSWORD)
    if password != verify_password:
        return response_fail(password_mismatch)
    old_password = body.get(OLD_PASSWORD)
    # check for old profile password
    auth_token = request.headers.get(HEADER_AUTH_TOKEN)
    profile = Profile.auth_token_filter(auth_token)
    if profile:
        # profile found changing password
        if old_password != profile.password:
            return response_fail(old_password_wrong)
        else:
            profile.password = password
            profile.save()
            return response_ok({PROFILE: profile.to_json()})
    else:
        return response_fail(device_not_exist)


def update_profile(request):
    pass


class CheckInResponse:
    profile: Profile
    settings: AppSettings

    def to_json(self):
        return {
            PROFILE: self.profile.to_json(),
            APP_SETTINGS: self.settings.to_json()
        }


class ValidPhonePayload:
    is_valid_msisdn: bool = True
    international_msisdn: str

    def to_json(self):
        return {
            IS_VALID_MSI_SDN: self.is_valid_msisdn,
            INTERNATIONAL_MSI_SDN: self.international_msisdn,
        }


@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(check_in_body_fields)
@csrf_exempt  # bypass validation for now
@require_POST
def checkin(request):
    # auth token is valid, proceeding
    # should return CheckInPayload(Profile, AppSettings)
    body = request.POST
    country_code = body.get(COUNTRY_CODE)
    auth_token = request.headers.get(HEADER_AUTH_TOKEN)
    settings = AppSettings.country_filter(country_code)
    print("Settings", settings)
    print("Settings", country_code)
    if not settings:
        return response_fail(country_code_not_available)
    profile = Profile.auth_token_filter(auth_token)
    if not profile:
        return response_fail(auth_token_not_valid)
    profile.country = get_country(iso_2_country_code="", iso_3=country_code)
    response = CheckInResponse()
    response.settings = settings
    response.profile = profile
    return response_ok(response.to_json())
    pass


def contact_sync(request):
    pass


@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields([MSI_SDN])
@csrf_exempt  # bypass validation for now
@require_POST
def check_valid_msisdn(request):
    body = request.POST
    phone = body.get(MSI_SDN)
    country_code = body.get(COUNTRY_CODE)
    verified_phone_number = check_valid_phone(phone, country_code)
    print("VER", verified_phone_number)
    if isinstance(verified_phone_number, HttpResponse):
        return verified_phone_number
    res = ValidPhonePayload()
    res.international_msisdn = verified_phone_number
    return response_ok(res.to_json())


def disconnect_social_account(request):
    pass
