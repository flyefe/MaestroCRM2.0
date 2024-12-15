# Generated by Django 5.1.2 on 2024-11-27 02:58

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contacts", "0007_remove_contactdetail_tags_alter_log_created_by_and_more"),
        (
            "segments",
            "0003_remove_segment_status_value_remove_segment_tag_value_and_more",
        ),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="segment",
            name="additional_rules",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="segment",
            name="contacts",
            field=models.ManyToManyField(
                blank=True, related_name="segments", to="contacts.contactdetail"
            ),
        ),
        migrations.AddField(
            model_name="segment",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    2024, 11, 27, 2, 57, 57, 234792, tzinfo=datetime.timezone.utc
                ),
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="segment",
            name="created_by",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="segments",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="segment",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
