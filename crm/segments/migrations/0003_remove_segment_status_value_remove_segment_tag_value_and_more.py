# Generated by Django 5.1.2 on 2024-11-27 02:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "segments",
            "0002_remove_segment_created_at_remove_segment_created_by_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="segment",
            name="status_value",
        ),
        migrations.RemoveField(
            model_name="segment",
            name="tag_value",
        ),
        migrations.AddField(
            model_name="segment",
            name="value",
            field=models.CharField(
                default=datetime.datetime(
                    2024, 11, 27, 2, 18, 28, 420934, tzinfo=datetime.timezone.utc
                ),
                max_length=50,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="segment",
            name="type",
            field=models.CharField(
                choices=[("STATUS", "status"), ("TAGS", "tags")],
                default="STATUS",
                max_length=50,
            ),
        ),
    ]
