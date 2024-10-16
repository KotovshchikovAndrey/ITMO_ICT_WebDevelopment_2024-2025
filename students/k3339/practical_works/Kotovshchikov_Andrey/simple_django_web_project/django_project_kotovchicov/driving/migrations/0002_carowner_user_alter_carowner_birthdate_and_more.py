# Generated by Django 5.1.2 on 2024-10-11 17:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("driving", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="carowner",
            name="user",
            field=models.OneToOneField(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="carowner",
            name="birthdate",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="ownership",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
