# Twilio config
twilio_account_sid = "AC1e9bc55c70c86a975e549bd545e55010"
twilio_auth_token = "3d8514be95e0a85b41eb7876cab43604"
twilio_phone_number = "+12344057755"
twilio_verification_body = "Your Memorify Project verification code is: "
# common response constants
SUCCESS = "SUCCESS"
FAIL = "FAIL"
PAYLOAD = "payload"
STATUS = "status"
MESSAGE = "message"
DEV_MESSAGE = "dev_message"
CONTENT_TYPE_JSON = "application/json"

# Payloads
APP_SETTINGS = "app_settings"
PROFILE = "profile"
GDPR = "gdpr"

# headers fields
HEADER_APP_VERSION = 'app-version'
HEADER_DEVICE_ID = 'device-id'
HEADER_DEVICE_TYPE = 'device-type'
HEADER_AUTH_TOKEN = 'auth-token'

# model properties - profile
NAME = "name"
PHONE = "phone"
PASSWORD = "password"
VERIFY_PASSWORD = "verify_password"
TIMEZONE = "user_timezone"
TIMEZONE_REGION = "user_timezone_region"
LANGUAGE = "language"
EMAIL = "email"
DEVICE_TOKEN = "device_token"
DEVICE_NAME = "device_name"
DEVICE_OS_VERSION = "device_os_version"
DEVICE_OEM = "device_oem"
MOBILE_CARRIER = "mobile_carrier"
APP_STORE_VERSION = "app_store_version"
IS_ROOTED = "is_rooted"
IS_EMULATOR = "is_emulator"
COUNTRY_CODE = "country_code"
VERIFICATION_CODE = "verification_code"
CONTACT_ACCESS = "contact_access"
IS_FIRST_LOADING = "is_first_loading"
APP_VERSION = 'app_version'
DEVICE_ID = 'device_id'
DEVICE_TYPE = 'device_type'
AUTH_TOKEN = 'auth_token'
MSI_SDN = "msisdn"
IS_VALID_MSI_SDN = "is_valid_msisdn"
INTERNATIONAL_MSI_SDN = "international_msisdn"
OLD_PASSWORD = "old_password"
EMAIL_PHONE = "email_phone"
VERIFICATION_TYPE = "verification_type"
FIREBASE_ERROR = "firebase_error"
OCCASION = "occasion"
MESSAGE_TYPE = "message_type"
RELEASE_AFTER_LIFE = "release_after_life"
RELEASE_DT = "release_dt"
AFTER_LIFE_VERIFICATION_TYPE = "after_life_verification_type"
CONTACTS_LIST = "contacts_list"
PUBLIC_ID = "public_id"
MOBILE = "mobile"
MESSAGE_PUBLIC_ID = "message_public_id"
PAGE_INDEX = "page_index"
CONTACT_PUBLIC_ID = "contact_public_id"

common_body_fields = [
    LANGUAGE,
    TIMEZONE,
    TIMEZONE_REGION,
    COUNTRY_CODE,
    APP_STORE_VERSION,
    MOBILE_CARRIER,
]

common_login_register_body_fields = common_body_fields + [
    PASSWORD,
    # DEVICE_TOKEN,
    DEVICE_NAME,
    DEVICE_OS_VERSION,
    DEVICE_OEM,
]

check_in_body_fields = common_body_fields + [
    DEVICE_TOKEN,
    IS_FIRST_LOADING,
    DEVICE_ID,
    DEVICE_TYPE,
    APP_VERSION,
]

registration_body_fields = common_login_register_body_fields + [
    NAME,
    PHONE,
    VERIFY_PASSWORD,
    # EMAIL,
    IS_ROOTED,
    IS_EMULATOR,
    VERIFICATION_CODE,
]

login_body_fields = common_login_register_body_fields + [
    EMAIL_PHONE,
]

common_phone_verification_fields = [
    MSI_SDN,
    COUNTRY_CODE
]

request_code_fields = common_phone_verification_fields + [
    VERIFICATION_TYPE,
    FIREBASE_ERROR
]

update_phone_fields = common_phone_verification_fields + [
    VERIFICATION_CODE
]

change_password_fields = [
    PASSWORD,
    VERIFY_PASSWORD,
    OLD_PASSWORD
]

send_message_body_fields = [
    OCCASION,
    MESSAGE_TYPE,
    RELEASE_AFTER_LIFE,
    # RELEASE_DT, mandatory in case release after life false
    AFTER_LIFE_VERIFICATION_TYPE,
    CONTACTS_LIST,
]
# error messages
headers_fields_required = "Headers fields are all missing"
body_fields_required = "Body fields are all missing"
missing_headers_fields = "Missing headers fields: "
missing_body_fields = "Missing body fields: "
version_required = f"Missing {HEADER_APP_VERSION} in headers"
device_id_required = f"Missing {HEADER_DEVICE_ID} in headers"
device_not_exist = "Device does not exist"
device_type_required = f"Missing {HEADER_DEVICE_TYPE} in headers"
auth_token_required = f"Missing {HEADER_AUTH_TOKEN} in headers"
auth_token_not_valid = f"{HEADER_AUTH_TOKEN} is not valid"
country_code_required = f"{COUNTRY_CODE} field must not be empty"
country_code_not_available = f"{COUNTRY_CODE} field is not available"
invalid_verification_code = 'Verification code is not correct'
password_mismatch = 'Password does not match'
old_password_wrong = 'The current password is wrong'
device_not_allowed = ' devices are not allowed to enter the app'
rooted_device_not_allowed = f'Rooted{device_not_allowed}'
emulator_device_not_allowed = f'Emulators{device_not_allowed}'
invalid_phone_number = 'Phone number is not valid'
invalid_email = 'Email address is not valid'
wrong_credentials = 'Wrong Credentials'
