# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from datetime import date

import pytest
from rest_framework.test import APIClient

from tms.models import Customer, TransportOrder, Vehicle


@pytest.mark.django_db
def test_create_transport_order_via_api():
    customer = Customer.objects.create(name="Autohaus Mueller")
    vehicle = Vehicle.objects.create(
        vin="WBA123456789ABCDE",
        brand="BMW",
        model="i4",
        current_location="Duesseldorf",
    )
    client = APIClient()

    response = client.post(
        "/api/orders/",
        {
            "customer": customer.id,
            "vehicle": vehicle.id,
            "pickup_location": "Duesseldorf",
            "delivery_location": "Muenchen",
            "requested_pickup_date": date(2026, 6, 12).isoformat(),
            "requested_delivery_date": date(2026, 6, 14).isoformat(),
            "priority": "high",
        },
        format="json",
    )

    assert response.status_code == 201
    assert TransportOrder.objects.count() == 1


@pytest.mark.django_db
def test_ai_create_order_draft_creates_domain_objects():
    client = APIClient()

    response = client.post(
        "/api/ai/create-order-draft/",
        {
            "draft": {
                "customer_name": "Autohaus Mueller",
                "vehicle_brand": "BMW",
                "vehicle_model": "i4",
                "vin": "WBA123456789ABCDE",
                "pickup_location": "Duesseldorf",
                "delivery_location": "Muenchen",
                "requested_pickup_date": "2026-06-12",
                "requested_delivery_date": "2026-06-14",
                "priority": "normal",
                "notes": "Created from test.",
            }
        },
        format="json",
    )

    assert response.status_code == 201
    assert Customer.objects.filter(name="Autohaus Mueller").exists()
    assert Vehicle.objects.filter(vin="WBA123456789ABCDE", status="assigned").exists()
    assert TransportOrder.objects.filter(created_by_ai=True).exists()


@pytest.mark.django_db
def test_tool_calling_endpoint_returns_unassigned_vehicles():
    Vehicle.objects.create(
        vin="WAUZZZ8V1KA123456",
        brand="Audi",
        model="Q4 e-tron",
        current_location="Ingolstadt",
    )
    client = APIClient()

    response = client.post(
        "/api/ai/query-orders/",
        {"message": "Welche Fahrzeuge sind noch nicht disponiert?"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["tool"] == "get_unassigned_vehicles"
    assert response.data["data"][0]["vin"] == "WAUZZZ8V1KA123456"
