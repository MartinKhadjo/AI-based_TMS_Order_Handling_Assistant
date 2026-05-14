# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

import re
from dataclasses import dataclass
from datetime import date
from typing import Any


REQUIRED_DRAFT_FIELDS = [
    "customer_name",
    "vehicle_brand",
    "vehicle_model",
    "vin",
    "pickup_location",
    "delivery_location",
]


@dataclass
class DraftValidationResult:
    missing_fields: list[str]
    validation_errors: list[str]
    warnings: list[str]

    @property
    def is_valid(self) -> bool:
        return not self.missing_fields and not self.validation_errors


class ValidationService:
    @staticmethod
    def validate_draft(draft: dict[str, Any]) -> DraftValidationResult:
        missing_fields = [
            field
            for field in REQUIRED_DRAFT_FIELDS
            if not str(draft.get(field, "")).strip()
        ]
        validation_errors: list[str] = []
        warnings: list[str] = []

        vin = str(draft.get("vin", "")).strip().upper()
        if vin and not re.fullmatch(r"[A-HJ-NPR-Z0-9]{8,17}", vin):
            validation_errors.append(
                "VIN must contain 8 to 17 allowed alphanumeric characters without I, O or Q."
            )
        elif vin and len(vin) != 17:
            warnings.append("VIN is accepted for the demo but real production VINs usually have 17 characters.")

        pickup_date = draft.get("requested_pickup_date")
        delivery_date = draft.get("requested_delivery_date")
        if pickup_date and delivery_date:
            try:
                pickup = date.fromisoformat(str(pickup_date))
                delivery = date.fromisoformat(str(delivery_date))
            except ValueError:
                validation_errors.append("Requested dates must use ISO format YYYY-MM-DD.")
            else:
                if delivery < pickup:
                    validation_errors.append("Delivery date cannot be earlier than pickup date.")

        return DraftValidationResult(
            missing_fields=missing_fields,
            validation_errors=validation_errors,
            warnings=warnings,
        )
