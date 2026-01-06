from django.contrib import admin
from .models import Form, FormField, FormResponse, FieldResponse

admin.site.register(Form)
admin.site.register(FormField)
admin.site.register(FormResponse)
admin.site.register(FieldResponse)
