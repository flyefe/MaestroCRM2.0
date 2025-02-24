from django.db import models
from contacts.models import Contact
from django.contrib.auth.models import User, Group

class InvoiceTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#000000")  # Hex color for UI representation

    def __str__(self):
        return self.name


class Invoice(models.Model):
    UNIT_MEASUREMENT_CHOICES = [("Quantity", "Quantity"), ("kg", "Weight (kg)"), ("CBM", "Volume (CBM)"), ("40ft Container", "Container"), ("20ft Container", "Container")]
    QUOTE_CURRENCY_CHOICES = [("₦", "NGN"), ("$", "USD"), ("¥", "Yuan")]
    STATUS_CHOICES = [
            ("Draft", "Draft"),
            ("Proforma Invoice", "Proforma Invoice"),
            ("Final Invoice", "Final Invoice"),
            ("Paid", "Paid"),
            ("Overdue", "Overdue")            
            ]

    
    company_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField()
    website_link = models.URLField(blank=True, null=True)
    company_logo_url = models.URLField(blank=True, null=True)
    Assign_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="invoices")


    unit_measurement = models.CharField(
        max_length=20,
        choices= UNIT_MEASUREMENT_CHOICES,
        default="Quantity"
    )

    quote_currency = models.CharField(
        max_length=10,
        choices=QUOTE_CURRENCY_CHOICES,
        default="NGN"
    )

    rate_naira_usd = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    rate_yuan_usd = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    rate_naira_yuan = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)

    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_vat = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    # status = models.ForeignKey(InvoiceStatus, on_delete=models.SET_NULL, null=True, related_name="invoices")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Draft",
    )
    tags = models.ManyToManyField(InvoiceTag, blank=True, related_name="invoices")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, related_name="invoices")

    def __str__(self):
        return f"Invoice #{self.id} - {self.company_name}"


class InvoiceItem(models.Model):
    UNIT_MEASUREMENT_CHOICES = [("Quantity", "Quantity"), ("kg", "Weight (kg)"), ("CBM", "Volume (CBM)"), ("40ft Container", "40ft Container"), ("20ft Container", "20ft Container")]
    CURRENCY_CHOICES = [("NGN", "NGN"), ("USD", "USD"), ("Yuan", "Yuan")]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    unit_measurement = models.CharField(
        max_length=20,
        choices= UNIT_MEASUREMENT_CHOICES,
        default="Quantity"
    )

    unit = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        default="NGN"
    )

    quote_currency_equivalent = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.title} - {self.unit} {self.unit_measurement}"
