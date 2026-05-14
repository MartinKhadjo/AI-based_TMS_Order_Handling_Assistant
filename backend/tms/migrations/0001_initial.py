# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

# Generated for the AI-native TMS demo.

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Carrier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=80)),
                ("active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                (
                    "company_type",
                    models.CharField(
                        choices=[
                            ("dealer", "Dealer"),
                            ("oem", "OEM"),
                            ("logistics", "Logistics"),
                            ("rental", "Rental"),
                            ("private", "Private"),
                        ],
                        default="dealer",
                        max_length=30,
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Vehicle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("vin", models.CharField(max_length=17, unique=True)),
                ("brand", models.CharField(max_length=80)),
                ("model", models.CharField(max_length=120)),
                ("length_m", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("height_m", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("weight_kg", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("available", "Available"),
                            ("assigned", "Assigned"),
                            ("in_transit", "In transit"),
                            ("delivered", "Delivered"),
                            ("blocked", "Blocked"),
                        ],
                        default="available",
                        max_length=30,
                    ),
                ),
                ("current_location", models.CharField(blank=True, max_length=255)),
            ],
            options={"ordering": ["brand", "model", "vin"]},
        ),
        migrations.CreateModel(
            name="TransportOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("pickup_location", models.CharField(max_length=255)),
                ("delivery_location", models.CharField(max_length=255)),
                ("requested_pickup_date", models.DateField(blank=True, null=True)),
                ("requested_delivery_date", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("planned", "Planned"),
                            ("in_transit", "In transit"),
                            ("delivered", "Delivered"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="open",
                        max_length=30,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("normal", "Normal"),
                            ("high", "High"),
                            ("express", "Express"),
                        ],
                        default="normal",
                        max_length=30,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("created_by_ai", models.BooleanField(default=False)),
                (
                    "carrier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transport_orders",
                        to="tms.carrier",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transport_orders",
                        to="tms.customer",
                    ),
                ),
                (
                    "vehicle",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transport_orders",
                        to="tms.vehicle",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="AIExtractionLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("raw_input", models.TextField()),
                ("extracted_json", models.JSONField(default=dict)),
                ("confidence_score", models.DecimalField(decimal_places=2, default=0, max_digits=4)),
                ("validation_errors", models.JSONField(blank=True, default=list)),
                (
                    "transport_order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="ai_extraction_logs",
                        to="tms.transportorder",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("invoice_number", models.CharField(max_length=80, unique=True)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="EUR", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("issued", "Issued"),
                            ("paid", "Paid"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=30,
                    ),
                ),
                ("issued_at", models.DateField(blank=True, null=True)),
                (
                    "transport_order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoice",
                        to="tms.transportorder",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="TrackingEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("pickup_planned", "Pickup planned"),
                            ("picked_up", "Picked up"),
                            ("in_transit", "In transit"),
                            ("delivered", "Delivered"),
                            ("exception", "Exception"),
                        ],
                        max_length=40,
                    ),
                ),
                ("location", models.CharField(blank=True, max_length=255)),
                ("timestamp", models.DateTimeField()),
                ("description", models.TextField(blank=True)),
                (
                    "transport_order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tracking_events",
                        to="tms.transportorder",
                    ),
                ),
            ],
            options={"ordering": ["-timestamp"]},
        ),
    ]
