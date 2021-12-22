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
            "app_settings": {
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

    def __str__(self):
        return "country"


class Profile(document.Document):
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

    def __str__(self):
        return "Profile"

    def to_json(self, *args, **kwargs):
        json = {
            "full_name": self.full_name,
            "public_id": self.public_id,
            "original_phone": self.original_phone,
            "phone": self.phone,
            "number_verified": self.number_verified,
            "registration_ts": self.registration_ts,
            "country": self.country,
            "language": self.language,
            "is_active": self.is_active,
            "last_access_ts": self.last_access_ts,
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

    # class User(document.Document):


#     auth_token = fields.StringField()
#     profile = fields.EmbeddedDocumentField(Profile)
#     is_new_user = fields.BooleanField()
#     meta = {'collection': 'User'}
#
#     def __str__(self):
#         return self.auth_token + " >> " + self.profile + " " + self.is_new_user


# Message Related models
class Media(document.EmbeddedDocument):
    public_id = fields.StringField()
    message_public_id = fields.StringField()
    thumbnail_path = fields.StringField()
    pre_signed_url = fields.StringField()
    type = fields.StringField()

    def __str__(self):
        return "media"


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
    from_user = fields.EmbeddedDocumentField(MessageUser)
    to_contact = fields.EmbeddedDocumentField(MessageUser)
    occasion = fields.StringField()
    type = fields.StringField()
    created_dt = fields.DateTimeField()
    release_dt = fields.DateTimeField()
    read_dt = fields.DateTimeField()
    updated_dt = fields.DateTimeField()
    release_after_life = fields.BooleanField()
    after_life_verification_type = fields.StringField()
    is_locked = fields.BooleanField()
    verifying = fields.BooleanField()
    comments_count = fields.IntField()
    media_length = fields.IntField()
    thumbnail_path = fields.StringField()
    video_path = fields.StringField()
    receivers_list = fields.EmbeddedDocumentListField(MessageUser)
    # secured message
    text = fields.StringField()
    after_life_code = fields.IntField()
    audio_path = fields.StringField()
    pre_signed_url = fields.StringField()
    media_list = fields.EmbeddedDocumentListField(Media)


class Package(document.EmbeddedDocument):
    package_id = fields.StringField()
    amount = fields.StringField()
    price = fields.StringField()
    package_key = fields.StringField()
    duration = fields.StringField()


class ShopItem(document.Document):
    package_type = fields.StringField()
    packages_list = fields.EmbeddedDocumentListField(Package)
