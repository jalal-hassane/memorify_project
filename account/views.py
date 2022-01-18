import uuid

import requests
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from account.models import CheckInResponse, ValidPhonePayload, ContactSyncPayload, ResultStats
from memorify_app.firebase_config import storage, auth
from memorify_app.models import AppSettings, Profile, Contact
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


@csrf_exempt
@validate_headers()
@validate_body_fields([FIREBASE_TOKEN])
@require_POST
def firebase_email_verification(request):
    auth_token = request.headers.get(HEADER_AUTH_TOKEN)
    body = request.POST
    token = body[FIREBASE_TOKEN]
    response = auth.get_account_info(token)
    user = response['users'][0]
    # save profile and return profile payload to user
    if user['emailVerified']:
        email = user['email']
        profile = Profile.auth_token_filter(auth_token)
        profile.email = email
        profile.save()
        usr = "" \
              "Hello"
        return response_ok({PROFILE: profile.to_json()})
    return response_fail("Email verification failed")


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


def check_common_model_list(m_json):
    print("J_OBJ", m_json)
    is_valid = True
    keys = [LABEL, VALUE]
    for obj in m_json:
        for k in keys:
            print("KEY", k)
            if k not in obj.keys():
                is_valid = False
                break

    return is_valid


def check_address_model_list(m_json):
    print("J_OBJ", m_json)
    is_valid = True
    keys = [LABEL, STREET, CITY, POSTAL_CODE, COUNTRY]
    for obj in m_json:
        for k in keys:
            print("KEY", k)
            if k not in obj.keys():
                is_valid = False
                break
    return is_valid


def validate_contacts(c_list, profile_public_id):
    """
    :param profile_public_id
    :param c_list: list of contacts
    :return: ContactSyncPayload
    """
    contact_fields = [
        C_ID,
        IS_DELETED,
        NAME_PREFIX,
        FIRST_NAME,
        MIDDLE_NAME,
        FAMILY_NAME,
        NICKNAME,
        EMAILS,
        PHONES,
        JOB_TITLE,
        DEPARTMENT_NAME,
        ORGANIZATION_NAME,
        NAME_SUFFIX,
        PHONETIC_GIVEN_NAME,
        PHONETIC_MIDDLE_NAME,
        PHONETIC_FAMILY_NAME,
        PHONETIC_ORGANIZATION_NAME,
        ADDRESSES,
        URLS,
        BIRTHDAY,
        NOTE,
        INSTANT_MESSAGE_ADDRESSES
    ]
    received = 0
    valid = 0
    not_valid = 0
    added = 0
    updated = 0
    deleted = 0
    valid_contacts = []
    for c in c_list:
        received += 1
        print("CONTACT", c)
        all_fields_exist = True
        print("KEYS", c.keys())
        for k in contact_fields:
            print("KEY", k)
            if k not in c.keys():
                all_fields_exist = False
                break

        if not all_fields_exist:
            not_valid += 1
            continue

        phones = c[PHONES]
        if phones == '[]':
            phones = []
        else:
            all_fields_exist = check_common_model_list(phones)
            if not all_fields_exist:
                not_valid += 1
                continue

        emails = c[EMAILS]
        if emails == '[]':
            emails = []
        else:
            all_fields_exist = check_common_model_list(emails)
            if not all_fields_exist:
                not_valid += 1
                continue

        urls = c[URLS]
        if urls == '[]':
            urls = []
        else:
            all_fields_exist = check_common_model_list(urls)
            if not all_fields_exist:
                not_valid += 1
                continue

        instant_message_addresses = c[INSTANT_MESSAGE_ADDRESSES]
        if instant_message_addresses == '[]':
            instant_message_addresses = []
        else:
            all_fields_exist = check_common_model_list(instant_message_addresses)
            if not all_fields_exist:
                not_valid += 1
                continue

        addresses = c[ADDRESSES]  # array of AddressModel
        if addresses == '[]':
            addresses = []
        else:
            all_fields_exist = check_address_model_list(addresses)
            if not all_fields_exist:
                not_valid += 1
                continue

        valid += 1
        local_id = str(c[C_ID])
        is_deleted = json.loads(c[IS_DELETED])
        name_prefix = c[NAME_PREFIX]
        first_name = c[FIRST_NAME]
        middle_name = c[MIDDLE_NAME]
        family_name = c[FAMILY_NAME]
        nickname = c[NICKNAME]
        job_title = c[JOB_TITLE]
        department_name = c[DEPARTMENT_NAME]
        organization_name = c[ORGANIZATION_NAME]
        name_suffix = c[NAME_SUFFIX]
        phonetic_given_name = c[PHONETIC_GIVEN_NAME]
        phonetic_middle_name = c[PHONETIC_MIDDLE_NAME]
        phonetic_family_name = c[PHONETIC_FAMILY_NAME]
        phonetic_organization_name = c[PHONETIC_ORGANIZATION_NAME]
        birthday = c[BIRTHDAY]
        note = c[NOTE]

        #  todo change filter to phone number
        if phones == "[]":
            continue
        old = Contact.local_id_profile_public_id_filter(local_id, profile_public_id)
        if not old:
            old = Contact()
            public_id = str(uuid.uuid4())
            old.public_id = public_id
            old.profile_public_id = profile_public_id
            added += 1
        else:
            if is_deleted:
                deleted += 1
            else:
                updated += 1

        old.local_id = str(local_id)
        old.is_deleted = is_deleted
        old.name_prefix = name_prefix
        old.first_name = first_name
        old.middle_name = middle_name
        old.family_name = family_name
        old.nickname = nickname
        old.emails = emails
        # todo handle the case when contact has multiple phones (each phone should be a document with same data)
        old.phones = phones
        old.job_title = job_title
        old.department_name = department_name
        old.organization_name = organization_name
        old.name_suffix = name_suffix
        old.phonetic_given_name = phonetic_given_name
        old.phonetic_middle_name = phonetic_middle_name
        old.phonetic_family_name = phonetic_family_name
        old.phonetic_organization_name = phonetic_organization_name
        old.addresses = addresses
        old.urls = urls
        old.birthday = birthday
        old.note = note
        old.instant_message_addresses = instant_message_addresses
        old.save()
        valid_contacts.append(old.synced_contact_json())

        # for phone in phones:
        #     print(phone["label"])
        #     print(phone["value"])
        #     # check for each phone if exist a contact
        #     old = Contact.phone_filter(phone["value"], profile_public_id)
        #     if not old:
        #         old = Contact()
        #         public_id = str(uuid.uuid4())
        #         old.public_id = public_id
        #         old.profile_public_id = profile_public_id
        #         added += 1
        #     else:
        #         if is_deleted:
        #             deleted += 1
        #         else:
        #             updated += 1
        #
        #     old.local_id = str(local_id)
        #     old.is_deleted = is_deleted
        #     old.name_prefix = name_prefix
        #     old.first_name = first_name
        #     old.middle_name = middle_name
        #     old.family_name = family_name
        #     old.nickname = nickname
        #     old.emails = emails
        #     # todo handle the case when contact has multiple phones (each phone should be a document with same data)
        #     old.phone = phone["value"]
        #     old.job_title = job_title
        #     old.department_name = department_name
        #     old.organization_name = organization_name
        #     old.name_suffix = name_suffix
        #     old.phonetic_given_name = phonetic_given_name
        #     old.phonetic_middle_name = phonetic_middle_name
        #     old.phonetic_family_name = phonetic_family_name
        #     old.phonetic_organization_name = phonetic_organization_name
        #     old.addresses = addresses
        #     old.urls = urls
        #     old.birthday = birthday
        #     old.note = note
        #     old.instant_message_addresses = instant_message_addresses
        #     old.save()
        #     valid_contacts.append(old.synced_contact_json())

    contact_sync_payload = ContactSyncPayload()
    contact_sync_payload.result_list = valid_contacts
    contact_sync_payload.result_stats = ResultStats()

    contact_sync_payload.result_stats.received_contacts = received
    contact_sync_payload.result_stats.valid_contacts = valid
    contact_sync_payload.result_stats.added_contacts = added
    contact_sync_payload.result_stats.updated_contacts = updated
    contact_sync_payload.result_stats.deleted_contacts = deleted
    return contact_sync_payload


@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields([CONTACTS])
@csrf_exempt  # bypass validation for now
@require_POST
def contact_sync(request):
    body = request.POST
    profile = Profile.auth_token_filter(request.headers[HEADER_AUTH_TOKEN])
    if not profile:
        return response_fail("Profile not found")

    contacts = body[CONTACTS]
    print("CONTACTS", contacts)
    # validate json
    c_list = json.loads(contacts)
    print("CONTACTS JSON", str(c_list))
    payload = validate_contacts(c_list, profile.public_id)
    return response_ok(payload.to_json())


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
