from dataclasses import dataclass

from django.db import models

# Create your models here.
from memorify_app.models import GdprPopup


class DynamicPopup:
    def to_json(self):
        return {}


@dataclass
class Gdpr:
    gdpr_popup: GdprPopup
    dynamic_popup: DynamicPopup
    show_gdpr_popup: bool = True
    show_dynamic_popup: bool = False

    def __init__(self, show_popup: bool, popup: GdprPopup, show_dynamic: bool, dynamic: DynamicPopup) -> None:
        self.show_gdpr_popup = show_popup
        self.gdpr_popup = popup
        self.show_dynamic_popup = show_dynamic
        self.dynamic_popup = dynamic

    def to_json(self):
        return {
            "gdpr": {
                "show_gdpr_popup": self.show_gdpr_popup,
                "gdpr_popup": self.gdpr_popup.to_json(),
                "show_dynamic_popup": self.show_dynamic_popup,
                "dynamic_popup": self.dynamic_popup.to_json()
            }
        }
