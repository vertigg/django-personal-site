# Generated by Django 2.2.28 on 2022-11-24 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mailbox',
            options={'verbose_name_plural': 'Mailboxes'},
        ),
    ]