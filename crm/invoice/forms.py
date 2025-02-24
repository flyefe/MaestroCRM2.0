from django import forms
from .models import Invoice, InvoiceItem, InvoiceTag
from contacts.models import Contact

class InvoiceForm(forms.ModelForm):
    contact = forms.CharField(
        label="Contact",
        widget=forms.TextInput(attrs={"id": "contact-autocomplete", "placeholder": "Search contact..."})
    )
    class Meta:
        model = Invoice
        fields = ["contact"]  # Include other invoice fields as needed
