# Generated by Django 3.0.5 on 2020-04-15 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='hours',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='time',
            field=models.TimeField(default='00:00:00'),
            preserve_default=False,
        ),
    ]
