# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from django.contrib import admin

from .models import AIExtractionLog, Carrier, Customer, Invoice, TrackingEvent, TransportOrder, Vehicle


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "company_type", "contact_email", "created_at")
    search_fields = ("name", "contact_email")
    list_filter = ("company_type",)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("vin", "brand", "model", "status", "current_location")
    search_fields = ("vin", "brand", "model", "current_location")
    list_filter = ("brand", "status")


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "phone", "active")
    search_fields = ("name", "contact_email")
    list_filter = ("active",)


class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 0


@admin.register(TransportOrder)
class TransportOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "vehicle",
        "pickup_location",
        "delivery_location",
        "status",
        "priority",
        "created_by_ai",
    )
    list_filter = ("status", "priority", "created_by_ai")
    search_fields = ("customer__name", "vehicle__vin", "pickup_location", "delivery_location")
    inlines = [TrackingEventInline]


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ("transport_order", "event_type", "location", "timestamp")
    list_filter = ("event_type",)
    search_fields = ("transport_order__vehicle__vin", "location", "description")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("transport_order", "invoice_number", "amount", "currency", "status", "issued_at")
    list_filter = ("status", "currency")
    search_fields = ("invoice_number", "transport_order__vehicle__vin")


@admin.register(AIExtractionLog)
class AIExtractionLogAdmin(admin.ModelAdmin):
    list_display = ("id", "confidence_score", "transport_order", "created_at")
    readonly_fields = ("created_at",)
    search_fields = ("raw_input", "extracted_json")
