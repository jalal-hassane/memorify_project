import json

from django.http import HttpResponse

from memorify_app.models import AppSettings

# Create your views here.
from memorify_app.views import *


# {country_code} needed here
@validate_headers
def app_settings(request):
    country_code = request.GET.get("country_code")
    if not country_code:
        return response_fail(country_code_required)
    print("Country code", country_code)
    settings = AppSettings.country_filter(country_code)
    print("Settings", settings)
    if not settings:
        return response_fail(country_code_not_available)
    return response_ok(settings)


def firebase_email_verification(request):
    pass


def change_password(request):
    pass


def update_profile(request):
    pass


# todo send required body fields to validation decorator
@validate_auth_token
@validate_body_fields([''])
def checkin(request):
    # auth token is valid, proceeding
    # should return CheckInPayload(Profile, AppSettings)
    pass


def contact_sync(request):
    pass


def check_valid_msisdn(request):
    pass


def disconnect_social_account(request):
    pass
