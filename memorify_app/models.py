from django.db import models
from mongoengine import document, fields


# Create your models here.
class User(document.Document):
    _id = fields.StringField(auto_created=True)
    name = fields.StringField()
    last_name = fields.StringField()
    phone = fields.StringField()
    meta = {'collection': 'User'}

    def __str__(self):
        return self._id + " >> " + self.name + " " + self.last_name + ": " + self.phone
