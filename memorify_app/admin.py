from django.contrib import admin

from memorify_app.models import *

# Register your models here.

admin.register(AppSettings)
admin.register(FirstGdprScreen)
admin.register(SecondGdprScreen)
admin.register(ConfirmationScreen)
admin.register(GdprPopup)
admin.register(Country)
admin.register(Profile)
admin.register(Media)
admin.register(MessageUser)
admin.register(Message)
admin.register(Package)
