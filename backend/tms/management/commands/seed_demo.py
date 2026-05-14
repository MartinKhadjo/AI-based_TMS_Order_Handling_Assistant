# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from tms.models import Carrier, Customer, TrackingEvent, TransportOrder, Vehicle


class Command(BaseCommand):
    help = "Create deterministic demo data for the AI-native TMS prototype."

    def handle(self, *args, **options):
        customer, _ = Customer.objects.get_or_create(
            name="Autohaus Mueller",
            defaults={"contact_email": "dispo@autohaus-mueller.example", "company_type": "dealer"},
        )
        second_customer, _ = Customer.objects.get_or_create(
            name="E-Mobility Fleet GmbH",
            defaults={"contact_email": "operations@emobility-fleet.example", "company_type": "rental"},
        )
        carrier, _ = Carrier.objects.get_or_create(
            name="Rhine Vehicle Logistics",
            defaults={"contact_email": "dispatch@rhine-logistics.example", "phone": "+49 211 123456"},
        )

        bmw, _ = Vehicle.objects.get_or_create(
            vin="WBA123456789ABCDE",
            defaults={
                "brand": "BMW",
                "model": "i4",
                "length_m": 4.78,
                "height_m": 1.45,
                "weight_kg": 2125,
                "status": Vehicle.Status.ASSIGNED,
                "current_location": "Duesseldorf",
            },
        )
        audi, _ = Vehicle.objects.get_or_create(
            vin="WAUZZZ8V1KA123456",
            defaults={
                "brand": "Audi",
                "model": "Q4 e-tron",
                "length_m": 4.59,
                "height_m": 1.63,
                "weight_kg": 2050,
                "status": Vehicle.Status.AVAILABLE,
                "current_location": "Ingolstadt",
            },
        )
        tesla, _ = Vehicle.objects.get_or_create(
            vin="5YJ3E1EA7KF123456",
            defaults={
                "brand": "Tesla",
                "model": "Model 3",
                "length_m": 4.69,
                "height_m": 1.44,
                "weight_kg": 1844,
                "status": Vehicle.Status.AVAILABLE,
                "current_location": "Berlin",
            },
        )

        order, _ = TransportOrder.objects.get_or_create(
            customer=customer,
            vehicle=bmw,
            pickup_location="Duesseldorf",
            delivery_location="Muenchen",
            defaults={
                "carrier": carrier,
                "requested_pickup_date": date.today() + timedelta(days=3),
                "requested_delivery_date": date.today() + timedelta(days=5),
                "status": TransportOrder.Status.PLANNED,
                "priority": TransportOrder.Priority.HIGH,
                "notes": "Seed order for the interview demo.",
                "created_by_ai": True,
            },
        )
        TrackingEvent.objects.get_or_create(
            transport_order=order,
            event_type=TrackingEvent.EventType.CREATED,
            defaults={
                "location": order.pickup_location,
                "timestamp": timezone.now(),
                "description": "Demo order created.",
            },
        )
        TrackingEvent.objects.get_or_create(
            transport_order=order,
            event_type=TrackingEvent.EventType.PICKUP_PLANNED,
            defaults={
                "location": order.pickup_location,
                "timestamp": timezone.now(),
                "description": "Carrier assigned for pickup.",
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data ready: "
                f"{Customer.objects.count()} customers, "
                f"{Vehicle.objects.count()} vehicles, "
                f"{TransportOrder.objects.count()} orders."
            )
        )
