from gdpr.models import Gdpr, DynamicPopup
from memorify_app.constants import GDPR
from memorify_app.models import GdprPopup, Device

# Create your views here.
from memorify_app.views import response_ok, validate_headers, response_fail, country_code_required, device_not_exist


@validate_headers()
def get(request):
    # gdpr_popup collection has only one document
    country_code = request.GET.get("country_code")
    if not country_code:
        return response_fail(country_code_required)
    popup = GdprPopup.objects.all().first()
    print("GDPR", popup)
    gdpr = Gdpr(show_popup=True, popup=popup, show_dynamic=False, dynamic=DynamicPopup())
    # save is_gdpr_applied in device collection
    old = Device.objects.filter(device_id=request.headers.get('device-id'))
    if old:
        print("OLD", old)
        device = old.first()
        device.app_version = request.headers.get('version')
        device.is_gdpr_applied = True
        device.save()
    return response_ok({GDPR: gdpr.to_json()})


@validate_headers()
def accept(request):
    old = Device.objects.filter(device_id=request.headers.get('device-id'))
    if old:
        return response_ok({})
    return response_fail(device_not_exist)


@validate_headers()
def update(request):
    body = request.GET
    if not body:
        return response_fail('Missing accepted_advertisement and accepted_support body fields')
    accepted_advertisement = body.get('accepted_advertisement')
    accepted_support = body.get('accepted_support')
    if not accepted_advertisement or not accepted_support:
        return response_fail('You should accept both support and advertisement')
    old = Device.objects.filter(device_id=request.headers.get('device-id'))
    if old:
        device = old.first()
        device.is_gdpr_applied = False
        device.save()
        return response_ok({})
    return response_fail(device_not_exist)


# functions below need auth_token
def delete_account(request):
    pass


def modify_account(request):
    pass


def export_data(request):
    pass
