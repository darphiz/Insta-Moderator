# Generated by Django 4.0.4 on 2022-05-19 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MAIN', '0012_instaaccounts_hast_two_fa'),
    ]

    operations = [
        migrations.RenameField(
            model_name='instaaccounts',
            old_name='hast_two_fa',
            new_name='has_two_factor',
        ),
    ]