# Generated by Django 2.0.2 on 2018-05-17 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0064_wfsettings_corrosive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discorduser',
            name='poe_profile',
            field=models.TextField(blank=True, default='', verbose_name='PoE Account'),
        ),
    ]