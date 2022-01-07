import requests
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from memorify_app.constants import HEADER_AUTH_TOKEN, verify_purchase_body_fields, PACKAGE_PUBLIC_ID, PURCHASE_TOKEN
from memorify_app.models import Package
from memorify_app.views import validate_body_fields, validate_headers, response_ok


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


@csrf_exempt  # bypass validation for now
@validate_headers(kwargs_=[HEADER_AUTH_TOKEN])
@validate_body_fields(verify_purchase_body_fields)
@require_POST
def verify_purchase(request):
    # todo integration with play google console
    body = request.POST
    package_name = 'app.memorify.com'
    product_id = body[PACKAGE_PUBLIC_ID]
    token = body[PURCHASE_TOKEN]
    validation_request = \
        requests.get("https://androidpublisher.googleapis.com/androidpublisher/v3/"
                     f"applications/{package_name}/purchases/products/{product_id}/tokens/{token}")
    print("Validation", validation_request)
    pass
