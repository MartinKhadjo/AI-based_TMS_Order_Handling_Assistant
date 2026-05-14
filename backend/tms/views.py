# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from decimal import Decimal

from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AIExtractionLog, Carrier, Customer, Invoice, TrackingEvent, TransportOrder, Vehicle
from .serializers import (
    AIExtractionLogSerializer,
    CarrierSerializer,
    CustomerSerializer,
    InvoiceSerializer,
    TrackingEventSerializer,
    TransportOrderSerializer,
    VehicleSerializer,
)
from .services.ai_extraction_service import AIExtractionService
from .services.order_service import OrderService
from .services.tool_calling_service import ToolCallingService
from .services.validation_service import ValidationService


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CarrierViewSet(viewsets.ModelViewSet):
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        vehicle_status = self.request.query_params.get("status")
        if vehicle_status:
            queryset = queryset.filter(status=vehicle_status)
        return queryset


class TransportOrderViewSet(viewsets.ModelViewSet):
    serializer_class = TransportOrderSerializer

    def get_queryset(self):
        queryset = (
            TransportOrder.objects.select_related("customer", "vehicle", "carrier")
            .prefetch_related("tracking_events")
            .all()
        )
        order_status = self.request.query_params.get("status")
        if order_status:
            queryset = queryset.filter(status=order_status)
        return queryset

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        order = self.get_object()
        next_status = request.data.get("status")
        valid_statuses = {choice[0] for choice in TransportOrder.Status.choices}
        if next_status not in valid_statuses:
            return Response(
                {"detail": f"Invalid status. Use one of: {sorted(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = next_status
        order.save(update_fields=["status", "updated_at"])

        # Keep vehicle availability aligned with the order lifecycle. In a real
        # TMS this prevents dispatching a vehicle that is already in transport.
        if next_status == TransportOrder.Status.IN_TRANSIT:
            order.vehicle.status = Vehicle.Status.IN_TRANSIT
            order.vehicle.save(update_fields=["status", "updated_at"])
        elif next_status == TransportOrder.Status.DELIVERED:
            order.vehicle.status = Vehicle.Status.DELIVERED
            order.vehicle.current_location = order.delivery_location
            order.vehicle.save(update_fields=["status", "current_location", "updated_at"])
        return Response(self.get_serializer(order).data)


class TrackingEventViewSet(viewsets.ModelViewSet):
    queryset = TrackingEvent.objects.select_related("transport_order").all()
    serializer_class = TrackingEventSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("transport_order").all()
    serializer_class = InvoiceSerializer


class AIExtractionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AIExtractionLog.objects.select_related("transport_order").all()
    serializer_class = AIExtractionLogSerializer


class DashboardAPIView(APIView):
    def get(self, request):
        orders_by_status = {
            item["status"]: item["count"]
            for item in TransportOrder.objects.values("status").annotate(count=Count("id"))
        }
        vehicles_by_status = {
            item["status"]: item["count"]
            for item in Vehicle.objects.values("status").annotate(count=Count("id"))
        }
        return Response(
            {
                "customers": Customer.objects.count(),
                "vehicles": Vehicle.objects.count(),
                "orders": TransportOrder.objects.count(),
                "open_orders": TransportOrder.objects.filter(status=TransportOrder.Status.OPEN).count(),
                "ai_created_orders": TransportOrder.objects.filter(created_by_ai=True).count(),
                "orders_by_status": orders_by_status,
                "vehicles_by_status": vehicles_by_status,
            }
        )


class ExtractOrderAPIView(APIView):
    def post(self, request):
        message = request.data.get("message", "")
        if not message.strip():
            return Response({"detail": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

        # The AI layer returns a draft only. It does not create customers,
        # vehicles or orders, so human review remains part of the workflow.
        result = AIExtractionService().extract_transport_order(message)

        # Store the raw input and extracted JSON for traceability. This makes it
        # possible to explain later what the AI suggested and which issues existed.
        AIExtractionLog.objects.create(
            raw_input=message,
            extracted_json=result.draft,
            confidence_score=Decimal(str(result.confidence)),
            validation_errors=result.validation_errors + result.missing_fields,
        )
        return Response(
            {
                "draft": result.draft,
                "missing_fields": result.missing_fields,
                "validation_errors": result.validation_errors,
                "warnings": result.warnings,
                "confidence": result.confidence,
                "provider": result.provider,
            }
        )


class CreateOrderDraftAPIView(APIView):
    def post(self, request):
        draft = request.data.get("draft")
        if not isinstance(draft, dict):
            return Response({"detail": "draft object is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate again at the write boundary. Frontend validation or previous
        # extraction results are helpful, but the backend owns data integrity.
        validation = ValidationService.validate_draft(draft)
        if not validation.is_valid:
            return Response(
                {
                    "missing_fields": validation.missing_fields,
                    "validation_errors": validation.validation_errors,
                    "warnings": validation.warnings,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # OrderService owns the transaction and the domain side effects:
            # customer/vehicle lookup, order creation, vehicle assignment and tracking.
            order = OrderService().create_order_from_draft(draft)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        raw_input = request.data.get("raw_input", draft.get("notes", ""))
        AIExtractionLog.objects.create(
            raw_input=raw_input,
            extracted_json=draft,
            confidence_score=Decimal(str(request.data.get("confidence", "0.90"))),
            validation_errors=[],
            transport_order=order,
        )
        return Response(TransportOrderSerializer(order).data, status=status.HTTP_201_CREATED)


class QueryOrdersAPIView(APIView):
    def post(self, request):
        message = request.data.get("message", "")
        if not message.strip():
            return Response({"detail": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

        # This deterministic router demonstrates tool-calling architecture
        # without depending on an external LLM during the interview demo.
        result = ToolCallingService().answer_operational_query(message)
        return Response(
            {
                "tool": result.tool,
                "arguments": result.arguments,
                "data": result.data,
                "answer": result.answer,
            }
        )
