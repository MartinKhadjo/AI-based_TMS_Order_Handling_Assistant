# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from django.core.validators import MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    # Shared audit fields keep every domain object traceable without repeating
    # created_at/updated_at declarations in each model.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Customer(TimeStampedModel):
    class CompanyType(models.TextChoices):
        DEALER = "dealer", "Dealer"
        OEM = "oem", "OEM"
        LOGISTICS = "logistics", "Logistics"
        RENTAL = "rental", "Rental"
        PRIVATE = "private", "Private"

    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField(blank=True)
    company_type = models.CharField(
        max_length=30,
        choices=CompanyType.choices,
        default=CompanyType.DEALER,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Carrier(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=80, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Vehicle(TimeStampedModel):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        ASSIGNED = "assigned", "Assigned"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"
        BLOCKED = "blocked", "Blocked"

    vin = models.CharField(max_length=17, unique=True)
    brand = models.CharField(max_length=80)
    model = models.CharField(max_length=120)
    length_m = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_m = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight_kg = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.AVAILABLE)
    current_location = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["brand", "model", "vin"]

    def __str__(self) -> str:
        return f"{self.brand} {self.model} ({self.vin})"


class TransportOrder(TimeStampedModel):
    # TransportOrder is the aggregate root of the demo: it connects customer,
    # vehicle, route, lifecycle status and AI origin in one business record.
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        PLANNED = "planned", "Planned"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        EXPRESS = "express", "Express"

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="transport_orders")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="transport_orders")
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transport_orders",
    )
    pickup_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)
    requested_pickup_date = models.DateField(null=True, blank=True)
    requested_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=30, choices=Priority.choices, default=Priority.NORMAL)
    notes = models.TextField(blank=True)
    created_by_ai = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk}: {self.vehicle.vin} {self.pickup_location} -> {self.delivery_location}"


class TrackingEvent(TimeStampedModel):
    class EventType(models.TextChoices):
        CREATED = "created", "Created"
        PICKUP_PLANNED = "pickup_planned", "Pickup planned"
        PICKED_UP = "picked_up", "Picked up"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"
        EXCEPTION = "exception", "Exception"

    transport_order = models.ForeignKey(
        TransportOrder,
        on_delete=models.CASCADE,
        related_name="tracking_events",
    )
    event_type = models.CharField(max_length=40, choices=EventType.choices)
    location = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.event_type} for order {self.transport_order_id}"


class Invoice(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    transport_order = models.OneToOneField(
        TransportOrder,
        on_delete=models.CASCADE,
        related_name="invoice",
    )
    invoice_number = models.CharField(max_length=80, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="EUR")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    issued_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.invoice_number


class AIExtractionLog(TimeStampedModel):
    # AI output is stored as an audit trail. The AI proposes structured data,
    # but confirmed domain objects are still created through backend services.
    raw_input = models.TextField()
    extracted_json = models.JSONField(default=dict)
    confidence_score = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    validation_errors = models.JSONField(default=list, blank=True)
    transport_order = models.ForeignKey(
        TransportOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_extraction_logs",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"AI extraction #{self.pk} ({self.confidence_score})"
