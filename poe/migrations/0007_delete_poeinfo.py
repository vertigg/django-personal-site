# Generated by Django 4.2.3 on 2023-10-04 06:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("poe", "0006_character_level_modified_at"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PoeInfo",
        ),
    ]