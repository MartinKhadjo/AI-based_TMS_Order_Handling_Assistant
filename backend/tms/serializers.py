# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from rest_framework import serializers

from .models import AIExtractionLog, Carrier, Customer, Invoice, TrackingEvent, TransportOrder, Vehicle


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "contact_email",
            "company_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = ["id", "name", "contact_email", "phone", "active", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "vin",
            "brand",
            "model",
            "length_m",
            "height_m",
            "weight_kg",
            "status",
            "current_location",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingEvent
        fields = [
            "id",
            "transport_order",
            "event_type",
            "location",
            "timestamp",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class TransportOrderSerializer(serializers.ModelSerializer):
    # Writes use foreign-key IDs; reads include nested details so the frontend
    # can render customer/vehicle information without extra API calls.
    customer_detail = CustomerSerializer(source="customer", read_only=True)
    vehicle_detail = VehicleSerializer(source="vehicle", read_only=True)
    carrier_detail = CarrierSerializer(source="carrier", read_only=True)
    tracking_events = TrackingEventSerializer(many=True, read_only=True)

    class Meta:
        model = TransportOrder
        fields = [
            "id",
            "customer",
            "customer_detail",
            "vehicle",
            "vehicle_detail",
            "carrier",
            "carrier_detail",
            "pickup_location",
            "delivery_location",
            "requested_pickup_date",
            "requested_delivery_date",
            "status",
            "priority",
            "notes",
            "created_by_ai",
            "tracking_events",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "transport_order",
            "invoice_number",
            "amount",
            "currency",
            "status",
            "issued_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class AIExtractionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIExtractionLog
        fields = [
            "id",
            "raw_input",
            "extracted_json",
            "confidence_score",
            "validation_errors",
            "transport_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
