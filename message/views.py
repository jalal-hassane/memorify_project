from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from memorify_app.constants import HEADER_AUTH_TOKEN, update_phone_fields, send_message_body_fields, RELEASE_AFTER_LIFE, \
    RELEASE_DT, missing_body_fields, OCCASION, CONTACTS_LIST, AFTER_LIFE_VERIFICATION_TYPE, MESSAGE_TYPE
from memorify_app.views import validate_body_fields, validate_headers, response_fail


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

    occasion = body.get(OCCASION)
    message_type = body.get(MESSAGE_TYPE)
    after_life_verification_type = body.get(AFTER_LIFE_VERIFICATION_TYPE)
    contacts_list = body.get(CONTACTS_LIST)

    pass


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(update_phone_fields)
@require_POST
def upload_media(request):
    pass


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(update_phone_fields)
@require_POST
def inbox(request):
    pass


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(update_phone_fields)
@require_POST
def outbox(request):
    pass


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(update_phone_fields)
@require_POST
def get_by_id(request):
    pass


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(update_phone_fields)
@require_POST
def delete_message(request):
    pass


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(update_phone_fields)
@require_POST
def submit_certificate(request):
    pass
