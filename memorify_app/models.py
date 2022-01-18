from datetime import datetime

from django.core.paginator import Paginator
from mongoengine import document, fields


# Create your models here.

class Device(document.Document):
    device_id = fields.StringField(default="")
    auth_token = fields.StringField(default="")
    type = fields.StringField(default="")
    model = fields.StringField(default="")
    os_version = fields.StringField(default="")
    app_version = fields.StringField(default="")
    app_store_version = fields.StringField(default="")
    manufacturer = fields.StringField(default="")
    operator = fields.StringField(default="")
    timezone = fields.StringField(default="")
    timezone_region = fields.StringField(default="")
    language = fields.StringField(default="")
    country_code = fields.StringField(default="")
    device_token = fields.StringField(default="")
    is_rooted = fields.BooleanField(default=False)
    is_emulator = fields.BooleanField(default=False)
    # should be true if user has declined advertisement and support
    is_gdpr_applied = fields.BooleanField(default=False)

    @staticmethod
    def device_id_filter(d_id: str):
        device = Device.objects.filter(device_id=d_id)
        if device:
            return device.first()
        else:
            return None

    @staticmethod
    def auth_token_filter(auth: str):
        device = Device.objects.filter(auth_token=auth)
        if device:
            return device.first()
        else:
            return None

    def __str__(self):
        return self.device_id


class AppSettings(document.Document):
    force_contact_sync = fields.BooleanField()
    message_max_characters = fields.IntField()
    comment_max_characters = fields.IntField()
    contacts_batch_size = fields.IntField()
    audio_max_seconds = fields.IntField()
    video_max_seconds = fields.IntField()
    video_min_seconds = fields.IntField()
    max_designated_survivors = fields.IntField()
    media_max_count = fields.IntField()
    send_to_contacts_max_count = fields.IntField()
    available_in_countries = fields.ListField()
    gdpr_applied_countries = fields.ListField()

    is_gdpr_applied = False

    def to_json(self):
        return {
            "force_contact_sync": self.force_contact_sync,
            "message_max_characters": self.message_max_characters,
            "comment_max_characters": self.comment_max_characters,
            "contacts_batch_size": self.contacts_batch_size,
            "audio_max_seconds": self.audio_max_seconds,
            "video_max_seconds": self.video_max_seconds,
            "video_min_seconds": self.video_min_seconds,
            "max_designated_survivors": self.max_designated_survivors,
            "media_max_count": self.media_max_count,
            "send_to_contacts_max_count": self.send_to_contacts_max_count,
            "is_gdpr_applied": self.is_gdpr_applied,
        }

    @staticmethod
    def country_filter(country_code: str):
        # app_settings collection contains only one document
        settings = AppSettings.objects.all().first()
        if country_code.upper() in settings.available_in_countries:
            for code in settings.gdpr_applied_countries:
                if country_code.lower() == code.lower():
                    settings.is_gdpr_applied = True
        else:
            return None
        return settings

    def __str__(self):
        return "settings"


class FirstGdprScreen(document.EmbeddedDocument):
    title = fields.StringField()
    description = fields.StringField()
    privacy_label = fields.StringField()
    privacy_link = fields.StringField()
    personal_data_label = fields.StringField()

    def __str__(self):
        return "First Gdpr screen"

    def to_json(self):
        return {
            "title": self.title,
            "description": self.description,
            "privacy_label": self.privacy_label,
            "privacy_link": self.privacy_link,
            "personal_data_label": self.personal_data_label,
        }


class SecondGdprScreen(document.EmbeddedDocument):
    title = fields.StringField()
    description = fields.StringField()
    label_1 = fields.StringField()
    label_2 = fields.StringField()
    label_3 = fields.StringField()
    footer = fields.StringField()

    def __str__(self):
        return "Second Gdpr screen"

    def to_json(self):
        return {
            "title": self.title,
            "description": self.description,
            "label_1": self.label_1,
            "label_2": self.label_2,
            "label_3": self.label_3,
            "footer": self.footer,
        }


class ConfirmationScreen(document.EmbeddedDocument):
    title = fields.StringField()
    description = fields.StringField()

    def __str__(self):
        return "Confirmation screen"

    def to_json(self):
        return {
            "title": self.title,
            "description": self.description,
        }


class GdprPopup(document.Document):
    first_screen = fields.EmbeddedDocumentField(FirstGdprScreen)
    second_screen = fields.EmbeddedDocumentField(SecondGdprScreen)
    first_confirmation_screen = fields.EmbeddedDocumentField(ConfirmationScreen)
    second_confirmation_screen = fields.EmbeddedDocumentField(ConfirmationScreen)
    delete_account_message = fields.StringField()
    already_deleted_message = fields.StringField()
    modify_account_message = fields.StringField()
    privacy_links = fields.StringField()
    accepted_support = fields.BooleanField()
    accepted_advertisement = fields.BooleanField()

    # meta = {'collection': 'GdprPopup'}
    def to_json(self):
        return {
            "first_screen": self.first_screen.to_json(),
            "second_screen": self.second_screen.to_json(),
            "first_confirmation_screen": self.first_confirmation_screen.to_json(),
            "second_confirmation_screen": self.second_confirmation_screen.to_json(),
            "delete_account_message": self.delete_account_message,
            "already_deleted_message": self.already_deleted_message,
            "modify_account_message": self.modify_account_message,
            "privacy_links": self.privacy_links,
            "accepted_support": self.accepted_support,
            "accepted_advertisement": self.accepted_advertisement,
        }


# class DynamicPopup(document.EmbeddedDocument):
#     pass
#
#
# class Gdpr(document.Document):
#     show_gdpr_popup = fields.BooleanField()
#     gdpr_popup = fields.EmbeddedDocumentField(GdprPopup)
#     show_dynamic_popup = fields.BooleanField()
#     dynamic_popup = fields.EmbeddedDocumentField(DynamicPopup)
#
#     def __str__(self):
#         return "GDPR"


class Country(document.Document):
    flag_url = fields.StringField()
    name = fields.StringField()
    code = fields.StringField()
    iso_2 = fields.StringField()

    def to_json(self):
        return {
            "flag_url": self.flag_url,
            "name": self.name,
            "code": self.code,
            "iso_2": self.iso_2,
        }

    def __str__(self):
        return "country"


class Profile(document.Document):
    auth_token = fields.StringField()
    full_name = fields.StringField()
    public_id = fields.StringField()
    original_phone = fields.StringField()
    phone = fields.StringField()
    password = fields.StringField()
    number_verified = fields.BooleanField()
    registration_ts = fields.DateTimeField()
    country = fields.DictField()
    language = fields.StringField()
    is_active = fields.BooleanField()
    last_access_ts = fields.DateTimeField()
    email = fields.EmailField()
    profile_image = fields.StringField()
    master_contact = fields.StringField()
    facebook_connected = fields.BooleanField()
    allowed_messages = fields.IntField()
    # fields below are only available when fb is connected
    username = fields.StringField()
    name = fields.StringField()

    # this field can ce changed

    def __str__(self):
        return "Profile"

    def to_json(self):
        json = {
            "full_name": self.full_name,
            "public_id": self.public_id,
            "original_phone": self.original_phone,
            "phone": self.phone,
            "number_verified": self.number_verified,
            "registration_ts": str(self.registration_ts),
            "country": self.country,
            "language": self.language,
            "is_active": self.is_active,
            "last_access_ts": str(self.last_access_ts),
            "email": self.email,
            "profile_image": self.profile_image,
            "master_contact": self.master_contact,
            "facebook_connected": self.facebook_connected,
            "allowed_messages": self.allowed_messages,
        }
        if self.username:
            json['username'] = self.username
        if self.name:
            json['name'] = self.name

        return json

    def to_message_user_json(self):
        return {
            "public_id": self.public_id,
            "phone": self.phone,
            "name": self.full_name,
            "profile_image": self.profile_image,
        }

    @staticmethod
    def auth_token_filter(auth: str):
        profile = Profile.objects.filter(auth_token=auth)
        if profile:
            return profile.first()
        else:
            return None

    @staticmethod
    def email_filter(email: str, password):
        profile = Profile.objects.filter(email=email, password=password)
        if profile:
            return profile.first()
        else:
            return None

    @staticmethod
    def phone_password_filter(phone: str, password):
        profile = Profile.objects.filter(original_phone=phone, password=password)
        if profile:
            return profile.first()
        else:
            return None

    @staticmethod
    def public_id_phone_filter(public_id, phone: str):
        profile = Profile.objects.filter(public_id=public_id, phone=phone)
        if profile:
            return profile.first()
        else:
            return None

    @staticmethod
    def get_public_id(auth_token):
        profile = Profile.auth_token_filter(auth_token)
        if not profile:
            return ""
        else:
            return profile.public_id


# Message Related models
class Media(document.Document):
    public_id = fields.StringField()
    message_public_id = fields.StringField()
    thumbnail_path = fields.StringField()
    pre_signed_url = fields.StringField()
    type = fields.StringField()

    def to_json(self):
        return {
            "public_id": self.public_id,
            "message_public_id": self.message_public_id,
            "thumbnail_path": self.thumbnail_path,
            "pre_signed_url": self.pre_signed_url,
            "type": self.type,
        }

    def __str__(self):
        return "media"


class DBMedia(document.Document):
    file = fields.FileField()
    public_id = fields.StringField()
    message_public_id = fields.StringField()
    thumbnail_path = fields.StringField()
    pre_signed_url = fields.StringField()
    type = fields.StringField()

    def to_json(self):
        return {
            "public_id": self.public_id,
            "message_public_id": self.message_public_id,
            "thumbnail_path": self.thumbnail_path,
            "pre_signed_url": self.pre_signed_url,
            "type": self.type,
        }

    def __str__(self):
        return "media"


# this class is not to be saved
class MessageUser(document.EmbeddedDocument):
    public_id = fields.StringField()
    phone = fields.StringField()
    name = fields.StringField()
    profile_image = fields.StringField()
    # case: from_user
    email = fields.StringField()

    def __str__(self):
        return "Message user"


class Message(document.Document):
    public_id = fields.StringField()
    from_user = fields.DictField()  # Message user dict
    to_contact = fields.DictField(null=True)  # to_contact is not important anymore
    occasion = fields.StringField()
    type = fields.StringField()
    created_dt = fields.DateTimeField(default=datetime.now())
    release_dt = fields.DateTimeField(null=True)
    read_dt = fields.DateTimeField(null=True)
    updated_dt = fields.DateTimeField(null=True)
    release_after_life = fields.BooleanField()
    after_life_verification_type = fields.StringField()
    is_locked = fields.BooleanField(default=False)
    verifying = fields.BooleanField(null=True)
    comments_count = fields.IntField(null=True)
    media_length = fields.IntField(default=0)
    thumbnail_path = fields.StringField(null=True)
    video_path = fields.StringField(null=True)
    receivers_list = fields.ListField()  # Message User
    # secured message
    text = fields.StringField(null=True)
    after_life_code = fields.IntField(null=True)
    audio_path = fields.StringField(null=True)
    pre_signed_url = fields.StringField(null=True)
    media_list = fields.ListField(null=True)  # Media

    def to_json(self, secured_message: bool = False):
        # check if message is locked every time we call this method
        if datetime.fromisoformat(self.release_dt) > datetime.now():
            self.is_locked = True
        else:
            self.is_locked = False
        self.save()
        json = {
            "public_id": self.public_id,
            "from_user": self.from_user,
            "to_contact": self.to_contact,
            "occasion": self.occasion,
            "type": self.type,
            "created_dt": str(self.created_dt),
            "release_after_life": self.release_after_life,
            "after_life_verification_type": self.after_life_verification_type,
            "is_locked": self.is_locked,
            "verifying": self.verifying,
            "comments_count": self.comments_count,
            "media_length": self.media_length,
            "thumbnail_path": self.thumbnail_path,
            "video_path": self.video_path,
            "receivers_list": self.receivers_list,
        }

        if self.release_dt:
            json["release_dt"] = str(self.release_dt)
        if self.read_dt:
            json["read_dt"] = str(self.read_dt)
        if self.updated_dt:
            json["updated_dt"] = str(self.updated_dt)
        if secured_message:
            if self.text:
                json["text"] = self.text
            if self.after_life_code:
                json["after_life_code"] = self.after_life_code
            if self.audio_path:
                json["audio_path"] = self.audio_path
            if self.pre_signed_url:
                json["pre_signed_url"] = self.pre_signed_url
            if self.media_list:
                json["media_list"] = [m for m in self.media_list]
        return json

    @staticmethod
    def public_id_filter(public_id):
        message = Message.objects.filter(public_id=public_id)
        if message:
            return message.first()
        else:
            return None

    @staticmethod
    def inbox(public_id, phone, page):
        results = []
        for message in Message.objects.all():
            for receiver in message.receivers_list:
                if receiver['public_id'] == public_id and receiver['phone'] == phone:
                    results.append(message.to_json())
                else:
                    pass
        paginator = Paginator(results, 10)
        if page not in paginator.page_range:
            return []
        data = paginator.page(page)
        return data.object_list

    @staticmethod
    def outbox(public_id, phone, page):
        results = [message.to_json() for message in Message.objects.all() if
                   message.from_user['public_id'] == public_id and message.from_user['phone'] == phone]
        paginator = Paginator(results, 10)
        if page not in paginator.page_range:
            return []
        data = paginator.page(page)
        return data.object_list


class Package(document.Document):
    package_id = fields.StringField()
    amount = fields.StringField()
    price = fields.StringField()
    package_key = fields.StringField()
    duration = fields.StringField()

    def to_json(self):
        return {
            "package_id": self.package_id,
            "amount": self.amount,
            "price": self.price,
            "package_key": self.package_key,
            "duration": self.duration,
        }


# RegisterResponse
class User:
    auth_token: str = ""
    profile: Profile
    is_new_user: bool = True
    meta = {'collection': 'User'}

    def __str__(self):
        return self.auth_token + " >> " + str(self.profile) + " " + str(self.is_new_user)

    def to_json(self):
        return {
            "auth_token": self.auth_token,
            "profile": self.profile.to_json(),
            "is_new_user": self.is_new_user,
        }


class Contact(document.Document):
    profile_public_id = fields.StringField()
    public_id = fields.StringField()
    local_id = fields.StringField()
    status = fields.StringField()
    is_deleted = fields.BooleanField()
    name_prefix = fields.StringField()
    first_name = fields.StringField()
    middle_name = fields.StringField()
    family_name = fields.StringField()
    nickname = fields.StringField()
    emails = fields.ListField()
    phones = fields.ListField()
    job_title = fields.StringField()
    department_name = fields.StringField()
    organization_name = fields.StringField()
    name_suffix = fields.StringField()
    phonetic_given_name = fields.StringField()
    phonetic_middle_name = fields.StringField()
    phonetic_family_name = fields.StringField()
    phonetic_organization_name = fields.StringField()
    addresses = fields.ListField()
    urls = fields.ListField()
    birthday = fields.StringField()
    note = fields.StringField()
    instant_message_addresses = fields.ListField()

    @staticmethod
    def phone_filter(phone):
        all_contacts = Contact.objects.all()
        for contact in all_contacts:
            if str(contact.phone) in phone or phone == str(contact.phone):
                return contact
        return None

    @staticmethod
    def local_id_profile_public_id_filter(local_id, profile_public_id):
        contact = Contact.objects.filter(local_id=local_id, profile_public_id=profile_public_id)
        if not contact:
            return None
        else:
            return contact.first()

    @staticmethod
    def phone_public_id_filter(phone, profile_public_id):
        all_contacts = Contact.objects.all()
        for contact in all_contacts:
            if str(contact.phone) in phone or phone in str(contact.phone):
                if contact.profile_public_id == profile_public_id:
                    return contact
        return None

    def synced_contact_json(self):
        return {
            "public_id": self.public_id,
            "local_id": self.local_id,
            "status": self.status,
            "deleted": self.is_deleted,
        }

    def to_message_user_json(self, phone):
        name = self.first_name + self.family_name
        return {
            "public_id": self.public_id,
            "phone": phone,
            "name": name,
            "profile_image": None,
        }


class GoogleAuthentication(document.Document):
    access_token = fields.StringField()
    expires_in = fields.IntField()
    refresh_token = fields.StringField()
    scope = fields.StringField()
    token_type = fields.StringField()

    def to_json(self):
        return {
            "access_token": self.access_token,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "token_type": self.token_type,
        }
