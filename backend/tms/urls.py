# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AIExtractionLogViewSet,
    CarrierViewSet,
    CreateOrderDraftAPIView,
    CustomerViewSet,
    DashboardAPIView,
    ExtractOrderAPIView,
    InvoiceViewSet,
    QueryOrdersAPIView,
    TrackingEventViewSet,
    TransportOrderViewSet,
    VehicleViewSet,
)


router = DefaultRouter()
router.register("customers", CustomerViewSet)
router.register("vehicles", VehicleViewSet)
router.register("carriers", CarrierViewSet)
router.register("orders", TransportOrderViewSet, basename="orders")
router.register("tracking-events", TrackingEventViewSet)
router.register("invoices", InvoiceViewSet)
router.register("ai/logs", AIExtractionLogViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    path("ai/extract-order/", ExtractOrderAPIView.as_view(), name="ai-extract-order"),
    path("ai/create-order-draft/", CreateOrderDraftAPIView.as_view(), name="ai-create-order-draft"),
    path("ai/query-orders/", QueryOrdersAPIView.as_view(), name="ai-query-orders"),
]
