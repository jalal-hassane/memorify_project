import requests
from django.http import HttpResponse
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from oauth2client.client import flow_from_clientsecrets

from memorify_app.constants import HEADER_AUTH_TOKEN, verify_purchase_body_fields, PACKAGE_PUBLIC_ID, PURCHASE_TOKEN
from memorify_app.models import Package, GoogleAuthentication
from memorify_app.views import validate_body_fields, validate_headers, response_ok, response_fail
from memorify_project.settings import GOOGLE_OAUTH2_CLIENT_SECRETS_JSON

FLOW = flow_from_clientsecrets(
    GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
    scope='https://www.googleapis.com/auth/gmail.readonly',
    redirect_uri='http://127.0.0.1:8000/oauth2callback',
    prompt='consent')


class ShopItem:
    package_type: str = "ONE_TIME"
    packages_list: list

    def to_json(self):
        return {
            "package_type": self.package_type,
            "packages_list": [p.to_json() for p in self.packages_list]
        }


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@require_POST
def get_store_packages(request):
    store_packages = Package.objects.all()
    shop = ShopItem()
    shop.packages_list = store_packages
    return response_ok({"shop_list": shop.to_json()})


def get_access_token(params):
    token_request = requests.post("https://accounts.google.com/o/oauth2/token", params=params)
    response = token_request.json()
    print("TOKEN REQ", response)
    if not response['error']:
        # success
        token_response = token_request.json()
        g_auth = GoogleAuthentication()
        g_auth.access_token = token_response['access_token']
        g_auth.expires_in = token_response['expires_in']
        g_auth.token_type = token_response['token_type']
        # refresh token
        if token_response['refresh_token']:
            g_auth.refresh_token = token_response['refresh_token']
        if token_response['scope']:
            g_auth.scope = token_response['scope']
        g_auth.save()
        return g_auth
    else:
        return response_fail("authentication failed")


def validate_inapp(body, access_token):
    package_name = 'com.loto.lotoapp2'
    product_id = body[PACKAGE_PUBLIC_ID]
    token = body[PURCHASE_TOKEN]
    req = requests.get("https://androidpublisher.googleapis.com/androidpublisher/v3/"
                       f"applications/{package_name}/purchases/products/{product_id}/tokens/{token}",
                       headers={'Content-Type': 'application/json',
                                'Authorization': 'Bearer {}'.format(access_token)})
    return req.json()


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(verify_purchase_body_fields)
@require_POST
def verify_purchase(request):
    # todo integration with play google console

    body = request.POST

    # check if google authentication has been saved before
    old_authentication = GoogleAuthentication.objects.all().first()
    if not old_authentication:
        # get access token
        params = {
            "grant_type": "authorization_code",
            "code": "4/2F0AX4XfWgE5u7QcA00gIi0yM7TAadu7ADVNnD9vcWQpBl6Hh_XmtI1oKo4xqeCyvkykJsiMQ",
            "client_id": '707893078045-0g5ds85lbtkd11pc015ap9i5c0f4fjs2.apps.googleusercontent.com',
            "client_secret": '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',
            "redirect_uri": "http://127.0.0.1:8000/oauth2callback"
        }
        old_authentication = get_access_token(params)
        if isinstance(old_authentication, HttpResponse):
            return old_authentication

    access_token = old_authentication.access_token
    validation_response = validate_inapp(body, access_token)

    print("Validation", validation_response)
    if validation_response['status'] == "UNAUTHENTICATED":
        # access token is expired, getting new one
        params = {
            "grant_type": "refresh_token",
            "client_id": '707893078045-0g5ds85lbtkd11pc015ap9i5c0f4fjs2.apps.googleusercontent.com',
            "client_secret": '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',
            "refresh_token": old_authentication.refresh_token
        }
        old_authentication = get_access_token(params)
        if isinstance(old_authentication, HttpResponse):
            return old_authentication

    access_token = old_authentication.access_token
    validation_response = validate_inapp(body, access_token)
    # successful response:
    """
        {
            "purchaseTimeMillis": "1641397155497", 
            "purchaseState": 0, 
            "consumptionState": 0, 
            "developerPayload": "", 
            "orderId": "GPA.3326-6001-5597-41742", 
            "purchaseType": 0, 
            "acknowledgementState": 1, 
            "kind": "androidpublisher#productPurchase", 
            "regionCode": "LB"
        }
    """
    if validation_response['purchaseState'] == 0:
        return response_ok("")
        pass

    return response_fail("Purchase token not valid")
