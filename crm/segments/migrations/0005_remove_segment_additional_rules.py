# Generated by Django 5.1.2 on 2024-11-27 02:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("segments", "0004_segment_additional_rules_segment_contacts_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="segment",
            name="additional_rules",
        ),
    ]
