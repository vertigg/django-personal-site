# Generated by Django 2.0.2 on 2018-03-30 10:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0035_auto_20180330_1314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discorduser',
            name='test_bool',
        ),
    ]