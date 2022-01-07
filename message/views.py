import json
import uuid
from datetime import datetime

import requests
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from memorify_app.constants import HEADER_AUTH_TOKEN, update_phone_fields, send_message_body_fields, RELEASE_AFTER_LIFE, \
    RELEASE_DT, missing_body_fields, OCCASION, CONTACTS_LIST, AFTER_LIFE_VERIFICATION_TYPE, MESSAGE_TYPE, PUBLIC_ID, \
    MOBILE, PAGE_INDEX, CONTACT_PUBLIC_ID
from memorify_app.firebase_config import storage
from memorify_app.models import Profile, Message, Media, Contact
from memorify_app.views import validate_body_fields, validate_headers, response_fail, response_ok, MESSAGE_PUBLIC_ID


# contacts: list of dictionary
# each dict should have public_id and mobile fields
# Returns False in case of error else returns list of profiles
def verify_contacts(contacts):
    receivers_json = []
    for c in contacts:
        public_id = c.get(PUBLIC_ID)
        phone = c.get(MOBILE)
        if not public_id or not phone:
            return response_fail("contacts_list: object should have public_id and mobile")
        else:
            profile = Profile.public_id_phone_filter(public_id, phone)
            if profile:
                receivers_json.append(profile.to_message_user_json())
            else:
                contact = Contact.phone_public_id_filter(phone, public_id)
                if contact:
                    receivers_json.append(contact.to_message_user_json(phone))
                else:
                    return response_fail("Profile was not found")
    return receivers_json


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(send_message_body_fields)
@require_POST
def send_message(request):
    body = request.POST
    release_after_life = bool(body.get(RELEASE_AFTER_LIFE))
    release_dt = body.get(RELEASE_DT)
    if not release_after_life:
        if not release_dt:
            # return response fail
            return response_fail(f"{missing_body_fields}{RELEASE_DT}")
    auth_token = request.headers.get(HEADER_AUTH_TOKEN)
    from_user_profile = Profile.auth_token_filter(auth_token)
    if not from_user_profile:
        return response_fail("User not found")

    # check if user has remaining messages to send
    if from_user_profile.allowed_messages == 0:
        return response_fail("User has no remaining messages to send")

    occasion = body.get(OCCASION)
    message_type = body.get(MESSAGE_TYPE)
    after_life_verification_type = body.get(AFTER_LIFE_VERIFICATION_TYPE)
    contacts_list = json.loads(body.get(CONTACTS_LIST))
    print(contacts_list)
    # create message object
    message = Message()
    message.public_id = str(uuid.uuid4())
    message.from_user = from_user_profile.to_message_user_json()
    message.occasion = occasion
    message.type = message_type
    message.after_life_verification_type = after_life_verification_type
    message.release_after_life = release_after_life
    message.release_dt = release_dt
    if release_after_life:
        message.is_locked = True
    else:
        # check date
        if datetime.fromisoformat(release_dt) > datetime.now():
            message.is_locked = True
        else:
            message.is_locked = False

    # verify contacts list: each object should contain public_id and mobile
    contacts_valid = verify_contacts(contacts_list)
    if isinstance(contacts_valid, HttpResponse):
        return contacts_valid
    message.receivers_list = contacts_valid
    message.save()
    remaining_count = from_user_profile.allowed_messages - 1
    from_user_profile.allowed_messages = remaining_count
    from_user_profile.save()

    print("MESSAGE", message.to_json())
    # todo send push to user if app installed else send message
    # return MessagePayload message: SecuredMessage, remaining_count: int
    return response_ok({
        "message": message.to_json(),
        "remaining_count": remaining_count
    })


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields([MESSAGE_PUBLIC_ID])
@require_POST
def upload_media(request):
    body = request.POST
    message_public_id = body.get(MESSAGE_PUBLIC_ID)
    print(message_public_id)
    message = Message.public_id_filter(message_public_id)
    if not message:
        return response_fail(f"Message with public_id: {message_public_id} was not found")
    files = request.FILES
    # should accept only one media at a time to handle error
    media = files.get("media_file")
    if not media:
        return response_fail(f"Missing files: media_file")
    print("FILE", media)
    if not message.media_list:
        # instantiate list
        message.media_list = list()

    # message can hold up to 30 media items
    if len(message.media_list) == 30:
        return response_fail("Max media items per message is 30")

    # todo create media file and upload it to firebase storage
    try:
        default_storage.save(media.name, media)
        storage_media_file = storage.child("media/" + media.name)
        storage_media_file.put("media/" + media.name)
        get_file_info = requests.get(
            f'https://firebasestorage.googleapis.com/v0/b/memorify-web.appspot.com/o/media%2F{media.name}',
            params=request.GET)

        file_info_json = json.loads(get_file_info.content)
        print("JSON", file_info_json)

        storage_file_path = "https://firebasestorage.googleapis.com/v0/b/memorify-web.appspot.com/o/media%2F" \
                            + media.name + "?alt=media&token=" + file_info_json["downloadTokens"]

        default_storage.delete(media.name)

        media_file = Media()
        media_file.public_id = str(uuid.uuid4())
        media_file.message_public_id = message_public_id
        media_file.thumbnail_path = "path"  # todo create thumbnail for video using ffmpeg
        media_file.pre_signed_url = storage_file_path
        media_file.type = file_info_json['contentType']
        media_file.save()

        # update media_list and save message
        # todo create presigned url and store media in the website
        message.media_list.append(media_file.to_json())
        message.media_length = message.media_length + 1
        message.save()
        print("No error occurred")
        return response_ok({})
    except:
        print("catching error")
        default_storage.delete(media.name)
        return response_fail("Upload error")


# todo add pagination to inbox and outbox
@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields([PAGE_INDEX])
@require_POST
def inbox(request):
    auth_token = request.headers[HEADER_AUTH_TOKEN]
    page_index = int(request.POST[PAGE_INDEX])
    profile = Profile.auth_token_filter(auth_token)
    if not profile:
        return response_fail("Profile not found")
    return response_ok({"inbox": Message.inbox(profile.public_id, profile.phone, page_index)})


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields([PAGE_INDEX])
@require_POST
def outbox(request):
    auth_token = request.headers[HEADER_AUTH_TOKEN]
    page_index = int(request.POST[PAGE_INDEX])
    profile = Profile.auth_token_filter(auth_token)
    if not profile:
        return response_fail("Profile not found")
    return response_ok({"outbox": Message.outbox(profile.public_id, profile.phone, page_index)})


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields([PUBLIC_ID])
@require_POST
def get_by_id(request):
    body = request.POST
    public_id = body[PUBLIC_ID]
    message = Message.public_id_filter(public_id)
    if not message:
        return response_fail(f"Message with public_id: {public_id} does not exist")
    return response_ok({"message": message.to_json(secured_message=True)})


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields([PUBLIC_ID])
@require_POST
def delete_message(request):
    """
    delete message
    :param request: body should have public_id (required) and contact_public_id (optional)
    if contact_public_id is omitted, delete message else only remove provided contact from receivers_list
    :return: HttpResponse
    """
    body = request.POST
    public_id = body[PUBLIC_ID]
    message = Message.public_id_filter(public_id)
    if not message:
        return response_fail(f"Message with public_id: {public_id} does not exist")
    contact_public_id = body.get(CONTACT_PUBLIC_ID)
    if contact_public_id:
        # remove contact from message
        for d in message.receivers_list:
            print("D", d)
            if d["public_id"] == contact_public_id:
                print("EQUAL")
                # check if receivers_list contains only one element
                if len(message.receivers_list) == 1:
                    message.delete()
                else:
                    message.receivers_list.remove(d)
                    message.save()
            else:
                pass
        print("message.receivers_list", message.receivers_list)
    else:
        # delete message
        message.delete()
    return response_ok({})


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields([MESSAGE_PUBLIC_ID])
@require_POST
def submit_certificate(request):
    body = request.POST
    message_public_id = body.get(MESSAGE_PUBLIC_ID)
    print(message_public_id)
    message = Message.public_id_filter(message_public_id)
    if not message:
        return response_fail(f"Message with public_id: {message_public_id} was not found")
    files = request.FILES
    # should accept only one media at a time to handle error
    media = files.get("death_certificate")
    if not media:
        return response_fail("Missing files: death_certificate")
    print("FILE", media)
    try:
        default_storage.save(media.name, media)
        storage_media_file = storage.child("death_certificate/" + media.name)
        storage_media_file.put("media/" + media.name)
        default_storage.delete(media.name)
        # todo save death certificate file in Message model
        return response_ok({})
    except:
        print("error")
        default_storage.delete(media.name)
        return response_fail("Unknown error")
