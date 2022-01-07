# Create your models here.
from memorify_app.constants import PROFILE, APP_SETTINGS, IS_VALID_MSI_SDN, INTERNATIONAL_MSI_SDN, LABEL, VALUE, STREET, \
    CITY, POSTAL_CODE, COUNTRY
from memorify_app.models import Profile, AppSettings


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


class CommonModel:
    label: str = ""
    value: str = ""

    def to_json(self):
        return {
            LABEL: self.label,
            VALUE: self.value
        }


class AddressModel:
    label: str = ""
    street: str = ""
    city: str = ""
    postalCode: str = ""
    country: str = ""

    def to_json(self):
        return {
            LABEL: self.label,
            STREET: self.street,
            CITY: self.city,
            POSTAL_CODE: self.postalCode,
            COUNTRY: self.country
        }


class ResultStats:
    received_contacts: int
    valid_contacts: int
    added_contacts: int
    updated_contacts: int
    deleted_contacts: int

    def to_json(self):
        return {
            "received_contacts": self.received_contacts,
            "valid_contacts": self.valid_contacts,
            "added_contacts": self.added_contacts,
            "updated_contacts": self.updated_contacts,
            "deleted_contacts": self.deleted_contacts
        }


class ContactSyncPayload:
    result_list: list
    result_stats: ResultStats

    def to_json(self):
        return {
            "result_list": [sc for sc in self.result_list],
            "result_stats": self.result_stats.to_json()
        }
