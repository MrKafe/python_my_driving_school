# Generated by Django 3.0.5 on 2020-04-13 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='Article',
        ),
    ]
