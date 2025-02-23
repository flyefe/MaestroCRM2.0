from django.contrib import admin
from .models import Invoice, InvoiceItem, InvoiceStatus, InvoiceTag

admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(InvoiceStatus)
admin.site.register(InvoiceTag)
