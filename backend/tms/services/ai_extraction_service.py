# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import Any

from django.conf import settings

from .validation_service import REQUIRED_DRAFT_FIELDS, ValidationService


@dataclass
class ExtractionResult:
    draft: dict[str, Any]
    missing_fields: list[str]
    validation_errors: list[str]
    warnings: list[str]
    confidence: float
    provider: str


class AIExtractionService:
    """Extracts structured transport order data from unstructured text.

    The default mock provider keeps the demo deterministic and key-free.
    The service boundary is intentionally shaped like a real AI adapter so
    an LLM provider can be added without touching views or the frontend.
    """

    def extract_transport_order(self, message: str) -> ExtractionResult:
        if settings.AI_MODE == "openai":
            return self._extract_with_openai(message)
        return self._extract_with_mock(message)

    def _extract_with_openai(self, message: str) -> ExtractionResult:
        # The interview demo is designed to run without external credentials.
        # Keeping this adapter explicit makes the production extension point clear.
        raise NotImplementedError(
            "AI_MODE=openai is a placeholder. Use AI_MODE=mock for the local demo."
        )

    def _extract_with_mock(self, message: str) -> ExtractionResult:
        draft: dict[str, Any] = {
            "customer_name": self._extract_customer(message),
            "vehicle_brand": None,
            "vehicle_model": None,
            "vin": self._extract_vin(message),
            "pickup_location": None,
            "delivery_location": None,
            "requested_pickup_date": None,
            "requested_delivery_date": None,
            "priority": self._extract_priority(message),
            "notes": message.strip(),
        }

        brand, model = self._extract_vehicle(message)
        draft["vehicle_brand"] = brand
        draft["vehicle_model"] = model

        pickup, delivery = self._extract_locations(message)
        draft["pickup_location"] = pickup
        draft["delivery_location"] = delivery

        pickup_date, delivery_date = self._extract_dates(message)
        draft["requested_pickup_date"] = pickup_date
        draft["requested_delivery_date"] = delivery_date

        validation = ValidationService.validate_draft(draft)
        confidence = self._calculate_confidence(draft, validation.validation_errors)

        return ExtractionResult(
            draft=draft,
            missing_fields=validation.missing_fields,
            validation_errors=validation.validation_errors,
            warnings=validation.warnings,
            confidence=confidence,
            provider="mock",
        )

    def _extract_customer(self, message: str) -> str | None:
        patterns = [
            r"\bKunde\s+(?:ist|:)\s+(?P<value>[^.\n,;]+)",
            r"\bCustomer\s+(?:is|:)\s+(?P<value>[^.\n,;]+)",
            r"\bfuer\s+(?P<value>Autohaus\s+[^.\n,;]+)",
            r"\bfor\s+(?P<value>[^.\n,;]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, message, flags=re.IGNORECASE)
            if match:
                return self._clean_value(match.group("value"))
        return None

    def _extract_vin(self, message: str) -> str | None:
        vin_match = re.search(r"\b(?:VIN\s*)?([A-HJ-NPR-Z0-9]{8,17})\b", message, re.IGNORECASE)
        if not vin_match:
            return None
        candidate = vin_match.group(1).upper()
        known_words = {"TRANSPORT", "ABHOLUNG", "LIEFERUNG", "CUSTOMER"}
        if candidate in known_words:
            return None
        return candidate

    def _extract_vehicle(self, message: str) -> tuple[str | None, str | None]:
        brands = [
            "Mercedes-Benz",
            "Volkswagen",
            "Porsche",
            "Hyundai",
            "Toyota",
            "Volvo",
            "Tesla",
            "Audi",
            "BMW",
            "Ford",
            "Opel",
            "Kia",
            "VW",
        ]
        for brand in brands:
            pattern = rf"\b{re.escape(brand)}\b\s*(?P<model>[A-Za-z0-9][A-Za-z0-9\- ]{{0,30}})?"
            match = re.search(pattern, message, flags=re.IGNORECASE)
            if match:
                raw_model = match.group("model") or ""
                model = re.split(
                    r"\b(?:mit|with|von|from|nach|to|VIN|Fahrgestellnummer)\b",
                    raw_model,
                    flags=re.IGNORECASE,
                )[0]
                return self._normalize_brand(brand), self._clean_value(model) or None
        return None, None

    def _extract_locations(self, message: str) -> tuple[str | None, str | None]:
        patterns = [
            r"\bvon\s+(?P<pickup>[^.\n,;]+?)\s+nach\s+(?P<delivery>[^.\n,;]+)",
            r"\bfrom\s+(?P<pickup>[^.\n,;]+?)\s+to\s+(?P<delivery>[^.\n,;]+)",
            r"\bAbholung\s+(?:in|bei)?\s*(?P<pickup>[^.\n,;]+).*?\bLieferung\s+(?:bis|nach|in)?\s*(?P<delivery>[^.\n,;]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, message, flags=re.IGNORECASE | re.DOTALL)
            if match:
                return (
                    self._clean_location(match.group("pickup")),
                    self._clean_location(match.group("delivery")),
                )
        return None, None

    def _extract_dates(self, message: str) -> tuple[str | None, str | None]:
        dates = []
        for match in re.finditer(r"\b(\d{4}-\d{2}-\d{2})\b", message):
            dates.append(match.group(1))
        for match in re.finditer(r"\b(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?\.?\b", message):
            day = int(match.group(1))
            month = int(match.group(2))
            year_text = match.group(3)
            if year_text:
                year = int(year_text)
                if year < 100:
                    year += 2000
            else:
                year = date.today().year
            try:
                dates.append(date(year, month, day).isoformat())
            except ValueError:
                continue
        pickup_date = dates[0] if dates else None
        delivery_date = dates[1] if len(dates) > 1 else None
        return pickup_date, delivery_date

    def _extract_priority(self, message: str) -> str:
        lowered = message.lower()
        if any(word in lowered for word in ["express", "urgent", "eilig", "dringend"]):
            return "express"
        if any(word in lowered for word in ["hoch", "high priority"]):
            return "high"
        return "normal"

    def _calculate_confidence(self, draft: dict[str, Any], validation_errors: list[str]) -> float:
        present_required = sum(1 for field in REQUIRED_DRAFT_FIELDS if draft.get(field))
        optional = sum(
            1
            for field in ["requested_pickup_date", "requested_delivery_date"]
            if draft.get(field)
        )
        score = (present_required / len(REQUIRED_DRAFT_FIELDS)) * 0.8 + optional * 0.1
        if validation_errors:
            score -= 0.2
        return round(max(0.0, min(score, 0.99)), 2)

    def _normalize_brand(self, brand: str) -> str:
        return "Volkswagen" if brand.upper() == "VW" else brand

    def _clean_value(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = re.sub(r"\s+", " ", value).strip(" .,:;-")
        return cleaned or None

    def _clean_location(self, value: str | None) -> str | None:
        cleaned = self._clean_value(value)
        if not cleaned:
            return None
        cleaned = re.split(
            r"\b(?:Abholung|Lieferung|Kunde|Customer|am|bis|on|by|mit|with|VIN)\b",
            cleaned,
            flags=re.IGNORECASE,
        )[0]
        return self._clean_value(cleaned)
