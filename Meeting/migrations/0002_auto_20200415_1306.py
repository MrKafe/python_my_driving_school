# Generated by Django 3.0.5 on 2020-04-15 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Meeting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='hours',
            field=models.TimeField(default='00:00:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meeting',
            name='location',
            field=models.TextField(null=True),
        ),
    ]
