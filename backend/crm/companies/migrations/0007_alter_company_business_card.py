# Generated by Django 4.2.3 on 2023-07-31 08:07

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("companies", "0006_alter_company_price_template"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="business_card",
            field=ckeditor.fields.RichTextField(blank=True, verbose_name="Визитка"),
        ),
    ]