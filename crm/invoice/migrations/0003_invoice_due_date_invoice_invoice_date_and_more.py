# Generated by Django 5.1.4 on 2025-02-25 04:54

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contacts", "0025_contact_company_name"),
        ("invoice", "0002_alter_invoice_status_alter_invoice_quote_currency_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="due_date",
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="invoice",
            name="invoice_date",
            field=models.DateField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="invoice",
            name="Assign_to",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="invoices",
                to="contacts.contact",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="company_logo_url",
            field=models.URLField(
                blank=True,
                default="https://g-linelogistics.com/wp-content/uploads/2023/03/Asset-2.png",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="created_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="invoices",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
