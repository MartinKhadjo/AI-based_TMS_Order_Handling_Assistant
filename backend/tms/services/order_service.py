# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from tms.models import Customer, TrackingEvent, TransportOrder, Vehicle

from .validation_service import ValidationService


class OrderService:
    @transaction.atomic
    def create_order_from_draft(self, draft: dict[str, Any]) -> TransportOrder:
        # Revalidate inside the transaction entrypoint. This protects the write
        # path even if a client bypasses the normal extraction endpoint.
        validation = ValidationService.validate_draft(draft)
        if not validation.is_valid:
            details = validation.missing_fields + validation.validation_errors
            raise ValueError("; ".join(details))

        # get_or_create keeps draft confirmation idempotent for known customers:
        # existing master data is reused instead of duplicated.
        customer, _ = Customer.objects.get_or_create(
            name=draft["customer_name"].strip(),
            defaults={
                "contact_email": draft.get("customer_email", ""),
                "company_type": draft.get("company_type", "dealer"),
            },
        )
        # VIN is the natural lookup key for the vehicle in this demo domain.
        vehicle, created = Vehicle.objects.get_or_create(
            vin=draft["vin"].strip().upper(),
            defaults={
                "brand": draft["vehicle_brand"].strip(),
                "model": draft["vehicle_model"].strip(),
                "current_location": draft.get("pickup_location", ""),
                "status": Vehicle.Status.AVAILABLE,
            },
        )
        if not created:
            vehicle.brand = draft.get("vehicle_brand") or vehicle.brand
            vehicle.model = draft.get("vehicle_model") or vehicle.model
            vehicle.current_location = draft.get("pickup_location") or vehicle.current_location
            vehicle.save(update_fields=["brand", "model", "current_location", "updated_at"])

        # Only after validation and master-data lookup do we persist the real
        # transport order. The created_by_ai flag preserves provenance.
        order = TransportOrder.objects.create(
            customer=customer,
            vehicle=vehicle,
            pickup_location=draft["pickup_location"].strip(),
            delivery_location=draft["delivery_location"].strip(),
            requested_pickup_date=draft.get("requested_pickup_date") or None,
            requested_delivery_date=draft.get("requested_delivery_date") or None,
            priority=draft.get("priority", TransportOrder.Priority.NORMAL),
            notes=draft.get("notes", ""),
            created_by_ai=True,
        )
        # Confirming a draft reserves the vehicle for this order.
        vehicle.status = Vehicle.Status.ASSIGNED
        vehicle.save(update_fields=["status", "updated_at"])
        # The first tracking event creates a visible lifecycle history from the
        # moment the AI-assisted draft becomes an operational order.
        TrackingEvent.objects.create(
            transport_order=order,
            event_type=TrackingEvent.EventType.CREATED,
            location=order.pickup_location,
            timestamp=timezone.now(),
            description="Order draft was confirmed and created from AI extraction.",
        )
        return order
