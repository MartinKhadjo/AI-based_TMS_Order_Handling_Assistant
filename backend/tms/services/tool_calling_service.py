# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from tms.models import TransportOrder, Vehicle


@dataclass
class ToolResult:
    tool: str
    arguments: dict[str, Any]
    data: Any
    answer: str


class ToolCallingService:
    """Tiny deterministic tool router that demonstrates MCP-style thinking."""

    def answer_operational_query(self, message: str) -> ToolResult:
        # The demo uses keyword routing so the behavior is explainable and
        # reproducible. A real LLM tool router could call the same private methods.
        lowered = message.lower()
        if any(term in lowered for term in ["nicht disponiert", "unassigned", "available", "frei"]):
            return self._get_unassigned_vehicles()
        if any(term in lowered for term in ["offene", "open order", "open orders", "auftraege", "aufträge"]):
            return self._get_open_transport_orders()
        order_id = self._extract_order_id(message)
        if order_id:
            return self._get_tracking_status(order_id)
        return ToolResult(
            tool="none",
            arguments={},
            data=[],
            answer=(
                "Ich konnte keine passende Demo-Tool-Anfrage erkennen. "
                "Versuche zum Beispiel: 'Welche Fahrzeuge sind nicht disponiert?'"
            ),
        )

    def _get_unassigned_vehicles(self) -> ToolResult:
        # Return dictionaries instead of model instances because API responses
        # should expose only the fields the tool needs.
        vehicles = list(
            Vehicle.objects.filter(status=Vehicle.Status.AVAILABLE)
            .order_by("brand", "model")
            .values("vin", "brand", "model", "current_location")
        )
        if not vehicles:
            answer = "Aktuell gibt es keine verfuegbaren, nicht disponierten Fahrzeuge."
        else:
            answer = "Nicht disponierte Fahrzeuge: " + "; ".join(
                f"{item['brand']} {item['model']} ({item['vin']}) in {item['current_location'] or 'unbekannt'}"
                for item in vehicles
            )
        return ToolResult(
            tool="get_unassigned_vehicles",
            arguments={},
            data=vehicles,
            answer=answer,
        )

    def _get_open_transport_orders(self) -> ToolResult:
        orders = list(
            TransportOrder.objects.filter(status__in=[TransportOrder.Status.OPEN, TransportOrder.Status.PLANNED])
            .select_related("customer", "vehicle")
            .order_by("requested_pickup_date", "-created_at")
        )
        data = [
            {
                "id": order.id,
                "customer": order.customer.name,
                "vin": order.vehicle.vin,
                "route": f"{order.pickup_location} -> {order.delivery_location}",
                "status": order.status,
                "requested_pickup_date": order.requested_pickup_date,
            }
            for order in orders
        ]
        if not data:
            answer = "Aktuell gibt es keine offenen oder geplanten Transportauftraege."
        else:
            answer = "Offene/geplante Auftraege: " + "; ".join(
                f"#{item['id']} {item['vin']} {item['route']} ({item['status']})"
                for item in data
            )
        return ToolResult(
            tool="get_open_transport_orders",
            arguments={},
            data=data,
            answer=answer,
        )

    def _get_tracking_status(self, order_id: int) -> ToolResult:
        order = (
            TransportOrder.objects.select_related("customer", "vehicle")
            .prefetch_related("tracking_events")
            .filter(pk=order_id)
            .first()
        )
        if not order:
            return ToolResult(
                tool="get_tracking_status",
                arguments={"order_id": order_id},
                data=None,
                answer=f"Transportauftrag #{order_id} wurde nicht gefunden.",
            )
        latest_event = order.tracking_events.first()
        data = {
            "id": order.id,
            "status": order.status,
            "vin": order.vehicle.vin,
            "route": f"{order.pickup_location} -> {order.delivery_location}",
            "latest_event": latest_event.event_type if latest_event else None,
            "latest_location": latest_event.location if latest_event else None,
        }
        answer = (
            f"Auftrag #{order.id} fuer VIN {order.vehicle.vin} ist im Status {order.status}. "
            f"Route: {order.pickup_location} -> {order.delivery_location}."
        )
        if latest_event:
            answer += f" Letztes Tracking: {latest_event.event_type} in {latest_event.location}."
        return ToolResult(
            tool="get_tracking_status",
            arguments={"order_id": order_id},
            data=data,
            answer=answer,
        )

    def _extract_order_id(self, message: str) -> int | None:
        match = re.search(r"#?(\d+)", message)
        return int(match.group(1)) if match else None
