"""memorify_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from account import views as account_views
from gdpr import views as gdpr_views
from memorify_project import settings
from register import views as register_views

API = 'api'
APP_SETTINGS = "app_settings"
EMAIL_VERIFICATION = "firebase_email_verification"
CHANGE_PASSWORD = "change_password"
UPDATE_PROFILE = "update_profile"
CHECKIN = "checkin"
CONTACT_SYNC = "contact_sync"
CHECK_VALID_MSISDN = "check_valid_msisdn"
DISCONNECT_SOCIAL_ACCOUNT = "disconnect_social_account"

LOGIN = "login"
REQUEST_CODE = "request_code"
REGISTER_USER = "register_user"
REGISTER_FACEBOOK = "facebook"
UPDATE_PHONE = "update_phone"

GET = "get"
ACCEPT = "accept"
UPDATE = "update"
DELETE_ACCOUNT = "delete_account"
MODIFY_ACCOUNT = "modify_account"
EXPORT_DATA = "export_data"

SEND_MESSAGE = "send_message"
UPLOAD_MEDIA = "upload_media"
INBOX = "inbox"
OUTBOX = "outbox"
GET_BY_ID = "get_by_id"
DELETE_MESSAGE = "delete_message"
SUBMIT_CERTIFICATE = "submit_certificate"

PURCHASE = "purchase"

MESSAGE = 'message/'
ACCOUNT = 'account/'
COMMENT = 'comment/'
COMMON = 'common/'
GDPR = 'gdpr/'
REGISTER = 'register/'
SHOP = 'shop/'

account_urls = [
    path(APP_SETTINGS, account_views.app_settings),
    path(EMAIL_VERIFICATION, admin.site.urls),
    path(CHANGE_PASSWORD, admin.site.urls),
    path(UPDATE_PROFILE, admin.site.urls),
    path(CHECKIN, admin.site.urls),
    path(CONTACT_SYNC, admin.site.urls),
    path(CHECK_VALID_MSISDN, admin.site.urls),
    path(DISCONNECT_SOCIAL_ACCOUNT, admin.site.urls),
]

message_urls = [
    path(SEND_MESSAGE, admin.site.urls),
    path(UPLOAD_MEDIA, admin.site.urls),
    path(INBOX, admin.site.urls),
    path(OUTBOX, admin.site.urls),
    path(GET_BY_ID, admin.site.urls),
    path(DELETE_MESSAGE, admin.site.urls),
    path(SUBMIT_CERTIFICATE, admin.site.urls),
]
comment_urls = []

gdpr_urls = [
    path(GET, gdpr_views.get),
    path(ACCEPT, gdpr_views.accept),
    path(UPDATE, admin.site.urls),
    path(DELETE_ACCOUNT, admin.site.urls),
    path(MODIFY_ACCOUNT, admin.site.urls),
    path(EXPORT_DATA, admin.site.urls),
]

register_urls = [
    path(LOGIN, admin.site.urls),
    path(REQUEST_CODE, admin.site.urls),
    path(REGISTER_USER, register_views.register),
    path(REGISTER_FACEBOOK, admin.site.urls),
    path(UPDATE_PHONE, admin.site.urls),
]
common_urls = []

shop_urls = [
    path(GET, admin.site.urls),
    path(PURCHASE, admin.site.urls),

]

api_urls = [
    path(ACCOUNT, include(account_urls)),
    path(MESSAGE, include(message_urls)),
    path(COMMENT, include(comment_urls)),
    path(GDPR, include(gdpr_urls)),
    path(REGISTER, include(register_urls)),
    path(COMMON, include(common_urls)),
    path(SHOP, include(shop_urls)),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
    path('administration/', include(api_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.FLAGS_URL,
                          document_root=settings.MEDIA_ROOT_FLAGS)
    urlpatterns += static(settings.PROFILE_PICTURES_URL,
                          document_root=settings.MEDIA_ROOT_PP)
