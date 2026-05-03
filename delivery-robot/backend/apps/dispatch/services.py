from apps.notifications.services import broadcast_order_update

from .models import RobotDispatch
from .providers import get_dispatch_provider


def trigger_dispatch_if_ready(order) -> None:
    if order.status != order.Status.READY:
        return

    provider_result = get_dispatch_provider().send_dispatch(order)
    dispatch, _ = RobotDispatch.objects.get_or_create(
        order=order,
        defaults={
            "provider": provider_result.provider,
            "status": provider_result.status,
            "request_payload": provider_result.request_payload,
            "response_payload": provider_result.response_payload,
        },
    )

    if dispatch.status != provider_result.status:
        dispatch.status = provider_result.status
        dispatch.provider = provider_result.provider
        dispatch.request_payload = provider_result.request_payload
        dispatch.response_payload = provider_result.response_payload
        dispatch.save(
            update_fields=["provider", "status", "request_payload", "response_payload", "updated_at"]
        )

    order.status = order.Status.DISPATCHED
    order.save(update_fields=["status", "updated_at"])
    broadcast_order_update(order)
