# Generated by Django 5.1.4 on 2024-12-30 04:20

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("contacts", "0016_contactdetail_email_contactdetail_first_name_and_more"),
        ("segments", "0013_segcategory_segment_category"),
        ("settings", "0007_tagcategory_tag_category"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ContactDetail",
            new_name="Contact",
        ),
    ]
