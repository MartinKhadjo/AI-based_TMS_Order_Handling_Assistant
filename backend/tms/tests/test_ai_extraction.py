# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

import pytest

from tms.services.ai_extraction_service import AIExtractionService


@pytest.mark.django_db
def test_mock_extraction_parses_core_transport_request():
    message = (
        "Bitte transportieren Sie einen BMW i4 mit VIN WBA123456789ABCDE "
        "von Duesseldorf nach Muenchen. Abholung am 12.06.2026, "
        "Lieferung bis 14.06.2026. Kunde ist Autohaus Mueller."
    )

    result = AIExtractionService().extract_transport_order(message)

    assert result.draft["customer_name"] == "Autohaus Mueller"
    assert result.draft["vehicle_brand"] == "BMW"
    assert result.draft["vehicle_model"] == "i4"
    assert result.draft["vin"] == "WBA123456789ABCDE"
    assert result.draft["pickup_location"] == "Duesseldorf"
    assert result.draft["delivery_location"] == "Muenchen"
    assert result.draft["requested_pickup_date"] == "2026-06-12"
    assert result.draft["requested_delivery_date"] == "2026-06-14"
    assert result.missing_fields == []
