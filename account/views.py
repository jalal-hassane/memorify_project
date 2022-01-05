import requests
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from memorify_app.firebase_config import storage
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


@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(update_profile_body_fields)
@csrf_exempt  # bypass validation for now
@require_POST
def update_profile(request):
    body = request.POST
    profile = Profile.auth_token_filter(request.headers[HEADER_AUTH_TOKEN])
    if not profile:
        return response_fail("No profile found for this auth token")
    try:
        remove_profile_pic = json.loads(body[REMOVE_PROFILE_PIC])
        print("Remove pic", remove_profile_pic)
    except ValueError:
        return response_fail("Value of remove_profile_pic must be boolean")

    if remove_profile_pic:
        print("Remove pic", remove_profile_pic)
        profile.profile_image = None
    else:
        # remove old profile picture and upload the new one
        files = request.FILES
        # should accept only one media at a time to handle error
        media = files.get("profile_picture")
        if not media:
            return response_fail("Missing files: profile_picture")
        print("FILE", media)
        try:
            default_storage.save(media.name, media)
            storage_media_file = storage.child("profile_pictures/" + media.name)
            storage_media_file.put("media/" + media.name)

            get_file_info = requests.get(
                f'https://firebasestorage.googleapis.com/v0/b/memorify-web.appspot.com/o/'
                f'profile_pictures%2F{media.name}', params=request.GET)

            file_info_json = json.loads(get_file_info.content)
            print("JSON", file_info_json)
            if str(file_info_json["contentType"]).startswith("video"):
                return response_fail("We only accept image as profile picture")

            storage_file_path = "https://firebasestorage.googleapis.com/v0/b/memorify-web.appspot.com/o/" \
                                "profile_pictures%2F" + media.name \
                                + "?alt=media&token=" + file_info_json["downloadTokens"]

            profile.profile_image = storage_file_path
            default_storage.delete(media.name)
        except:
            print("error")
            default_storage.delete(media.name)
            return response_fail("Unknown error")

    device_id = request.headers[HEADER_DEVICE_ID]
    auth_token = request.headers[HEADER_AUTH_TOKEN]
    app_version = request.headers[HEADER_APP_VERSION]
    update_device(device_id, body, app_version, auth_token)
    country_code = body[COUNTRY_CODE]
    profile.country = get_country(iso_2_country_code=country_code)
    profile.save()
    return response_ok({PROFILE: profile.to_json()})


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
    device = Device.auth_token_filter(auth_token)
    if not device:
        return response_fail(auth_token_not_valid)
    device_id = body[DEVICE_ID]
    app_version = body[APP_VERSION]
    update_device(device_id, body, app_version, auth_token)
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
