# Generated by Django 4.2.3 on 2023-07-18 06:36

import crm.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Company",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=150, verbose_name="Название Компании")),
                ("executive_name", models.CharField(max_length=150, verbose_name="ФИО исполняющего лица")),
                ("executive_position", models.CharField(max_length=150, verbose_name="Должность исполняющего лица")),
                ("address", models.CharField(max_length=150, verbose_name="Адрес")),
                ("logo_image", models.ImageField(upload_to="company-logos/", verbose_name="Логотип")),
                (
                    "signature_image",
                    models.ImageField(blank=True, null=True, upload_to="company-signatures/", verbose_name="Подпись"),
                ),
            ],
            options={
                "verbose_name_plural": "Companies",
            },
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("first_name", models.CharField(max_length=50, verbose_name="Имя")),
                ("middle_name", models.CharField(blank=True, max_length=50, verbose_name="Отчество")),
                ("last_name", models.CharField(max_length=50, verbose_name="Фамилия")),
                ("email", models.EmailField(blank=True, default="", max_length=254, verbose_name="Email адресс")),
                (
                    "phone_number",
                    models.CharField(
                        max_length=30,
                        validators=[crm.core.validators.validate_phone_number],
                        verbose_name="Номер телефона",
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="customers", to="companies.company"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Customers",
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("pid", models.CharField(max_length=50, verbose_name="Product ID")),
                ("name", models.CharField(max_length=150, verbose_name="Название")),
                ("data", models.JSONField(verbose_name="Параметры")),
                ("data_options", models.JSONField(blank=True, null=True, verbose_name="Дополнительные параметры")),
                ("price", models.PositiveIntegerField(blank=True, null=True, verbose_name="Цена розничная")),
                ("price_special", models.PositiveIntegerField(blank=True, null=True, verbose_name="Цена специальная")),
                ("url", models.URLField(verbose_name="Ссылка")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="products", to="companies.company"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Products",
            },
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("url", models.URLField(verbose_name="Ссылка")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="images", to="companies.product"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Product Images",
            },
        ),
        migrations.CreateModel(
            name="Deal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="deals", to="companies.customer"
                    ),
                ),
                (
                    "manager",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="deals", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="deals", to="companies.product"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Deals",
            },
        ),
        migrations.CreateModel(
            name="CompanyType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=50, verbose_name="Название")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="company_types",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Company Types",
            },
        ),
        migrations.AddField(
            model_name="company",
            name="company_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="companies.companytype",
                verbose_name="Тип Компании",
            ),
        ),
        migrations.CreateModel(
            name="CompanyProductLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=150, verbose_name="Название")),
                ("url", models.URLField(verbose_name="Ссылка")),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="links",
                        to="companies.company",
                        verbose_name="Компания",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Company Product Links",
                "unique_together": {("company", "url")},
            },
        ),
        migrations.CreateModel(
            name="CompanyMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="members", to="companies.company"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memberships",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Company Members",
                "unique_together": {("user", "company")},
            },
        ),
    ]
