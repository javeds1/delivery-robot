from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.utils import timezone


@dataclass(frozen=True)
class DispatchResult:
    provider: str
    status: str
    request_payload: dict[str, Any]
    response_payload: dict[str, Any]


class BaseDispatchProvider:
    provider_name = "robot"

    def send_dispatch(self, order) -> DispatchResult:
        raise NotImplementedError


class MockDispatchProvider(BaseDispatchProvider):
    provider_name = "robot"

    def send_dispatch(self, order) -> DispatchResult:
        request_payload = {
            "order_id": order.id,
            "pickup_location": order.vendor.location_label,
            "dropoff_location": order.delivery_location,
        }
        response_payload = {
            "message": "Mock dispatch accepted",
            "mock_delivery_enabled": settings.MOCK_DELIVERY_ENABLED,
            "state_mode": settings.MOCK_DELIVERY_STATE_MODE,
            "accepted_at": timezone.now().isoformat(),
        }
        return DispatchResult(
            provider=self.provider_name,
            status="SENT",
            request_payload=request_payload,
            response_payload=response_payload,
        )


class RealDispatchProvider(BaseDispatchProvider):
    provider_name = "fallback"

    def send_dispatch(self, order) -> DispatchResult:
        request_payload = {
            "order_id": order.id,
            "pickup_location": order.vendor.location_label,
            "dropoff_location": order.delivery_location,
        }
        response_payload = {
            "message": "Real provider not configured; falling back for temporary testing",
        }
        return DispatchResult(
            provider=self.provider_name,
            status="SENT",
            request_payload=request_payload,
            response_payload=response_payload,
        )


def get_dispatch_provider() -> BaseDispatchProvider:
    selected_provider = settings.DISPATCH_PROVIDER.lower()
    if selected_provider == "real":
        return RealDispatchProvider()
    return MockDispatchProvider()
