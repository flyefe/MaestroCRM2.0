from django.db import models
from django.contrib.auth.models import User
from contacts.models import Contact
from decouple import config
from django.core.validators import MinValueValidator

# Choices
UNIT_MEASUREMENT_CHOICES = [
    ("Quantity", "Quantity"),
    ("kg", "Weight (kg)"),
    ("CBM", "Volume (CBM)"),
    ("40ft Container", "Container"),
    ("20ft Container", "Container"),
]

QUOTE_CURRENCY_CHOICES = [
    ("₦", "NGN"),
    ("$", "USD"),
    ("¥", "Yuan"),
]

STATUS_CHOICES = [
    ("Draft", "Draft"),
    ("Proforma Invoice", "Proforma Invoice"),
    ("Final Invoice", "Final Invoice"),
    ("Paid", "Paid"),
    ("Overdue", "Overdue"),
]

CURRENCY_CHOICES = [
    ("NGN", "NGN"),
    ("USD", "USD"),
    ("Yuan", "Yuan"),
]

class InvoiceTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#000000")

    def __str__(self):
        return self.name

class Bank(models.Model):
    account_name = models.CharField(max_length=225)
    account_number = models.CharField(max_length=225)
    bank_name = models.CharField(max_length=225)

    def __str__(self):
        return f"{self.bank_name} - {self.account_name}"

class BusinessSettings(models.Model):
    business_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    telephone_number = models.CharField(max_length=20)
    website_url = models.URLField(blank=True, null=True)
    business_logo_url = models.URLField(blank=True, null=True, default=config('COMPANY_LOGO_URL', default=''))
    twitter_handle = models.CharField(max_length=100, blank=True, null=True)
    facebook_page = models.CharField(max_length=100, blank=True, null=True)
    linkedin_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Business Setting"
        verbose_name_plural = "Business Settings"

    def __str__(self):
        return self.business_name

class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length=10, choices=QUOTE_CURRENCY_CHOICES, default="NGN")
    target_currency = models.CharField(max_length=10, choices=QUOTE_CURRENCY_CHOICES)
    rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('base_currency', 'target_currency')

    def __str__(self):
        return f"{self.base_currency} to {self.target_currency}: {self.rate}"

class Invoice(models.Model):
    Assign_to = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, related_name="invoices")
    business_settings = models.ForeignKey(BusinessSettings, on_delete=models.SET_NULL, null=True, related_name="invoices")
    invoice_number = models.CharField(max_length=20, unique=True, editable=False, db_index=True)
    invoice_date = models.DateField(auto_now_add=True, db_index=True)
    due_date = models.DateField(null=True, blank=True)

    unit_measurement = models.CharField(max_length=20, choices=UNIT_MEASUREMENT_CHOICES, default="Quantity")
    quote_currency = models.CharField(max_length=10, choices=QUOTE_CURRENCY_CHOICES, default="NGN")

    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    total_vat = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft", db_index=True)
    tags = models.ManyToManyField(InvoiceTag, blank=True, related_name="invoices")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="invoices")

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-id').first()
            self.invoice_number = f"INV-{1000 + (last_invoice.id if last_invoice else 0) + 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.business_settings.business_name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    unit_measurement = models.CharField(max_length=20, choices=UNIT_MEASUREMENT_CHOICES, default="Quantity")
    unit = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])

    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="NGN")
    quote_currency_equivalent = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.amount = self.unit * self.price * (1 + self.tax_percentage / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.unit} {self.unit_measurement}"
