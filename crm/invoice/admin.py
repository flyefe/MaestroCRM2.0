from django.contrib import admin
from .models import Invoice, InvoiceItem, InvoiceTag, ExchangeRate, Bank, BusinessSettings

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'assigned_to', 'invoice_date', 'due_date', 'status', 'created_at')
    search_fields = ('invoice_number', 'assigned_to__first_name', 'assigned_to__last_name', 'status')
    list_filter = ('status', 'invoice_date', 'due_date')
    date_hierarchy = 'invoice_date'
    ordering = ('-created_at',)
    filter_horizontal = ('tags',)

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'title', 'unit', 'unit_measurement', 'price', 'currency', 'amount')
    search_fields = ('title', 'invoice__invoice_number')
    list_filter = ('unit_measurement', 'currency')

@admin.register(InvoiceTag)
class InvoiceTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'rate')
    search_fields = ('base_currency', 'target_currency')

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_name', 'account_number')
    search_fields = ('bank_name', 'account_name', 'account_number')

@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'contact_email', 'telephone_number', 'website_url')
    search_fields = ('business_name', 'contact_email')

