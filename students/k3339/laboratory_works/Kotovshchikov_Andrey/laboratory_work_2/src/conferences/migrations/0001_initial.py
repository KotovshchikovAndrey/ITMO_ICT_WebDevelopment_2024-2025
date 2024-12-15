# Generated by Django 5.1.2 on 2024-10-10 12:15

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "start_date",
                    models.DateTimeField(verbose_name="Дата начала бронирования"),
                ),
                (
                    "end_date",
                    models.DateTimeField(verbose_name="Дата окончания бронирования"),
                ),
            ],
            options={
                "verbose_name": "Бронь",
                "verbose_name_plural": "Доступная бронь",
                "db_table": "booking",
            },
        ),
        migrations.CreateModel(
            name="Conference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=255, verbose_name="Название конференции"
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="Описание конференции"
                    ),
                ),
                (
                    "participation_conditions",
                    models.TextField(
                        blank=True,
                        null=True,
                        verbose_name="Условия участия в конференции",
                    ),
                ),
                (
                    "is_publish",
                    models.BooleanField(
                        default=False, verbose_name="Рекомендован к публикации или нет"
                    ),
                ),
                (
                    "topics",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("MATH", "Математика"),
                                ("PHYSIC", "Физика"),
                                ("IT", "Информационные технологии"),
                            ],
                            max_length=15,
                        ),
                        default=list,
                        size=None,
                        verbose_name="Тематики",
                    ),
                ),
            ],
            options={
                "verbose_name": "Конференция",
                "verbose_name_plural": "Конференции",
                "db_table": "conference",
            },
        ),
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField(verbose_name="Текст комментария")),
                ("rating", models.PositiveSmallIntegerField(verbose_name="Рейтинг")),
            ],
            options={
                "verbose_name": "Комментарий",
                "verbose_name_plural": "Комментарии",
                "db_table": "feedback",
            },
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=20,
                        unique=True,
                        verbose_name="Название коференц зала",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="Описание конференц зала"
                    ),
                ),
                (
                    "seats",
                    models.PositiveSmallIntegerField(verbose_name="Количество мест"),
                ),
            ],
            options={
                "verbose_name": "Конференц зал",
                "verbose_name_plural": "Конференц залы",
                "db_table": "room",
            },
        ),
    ]