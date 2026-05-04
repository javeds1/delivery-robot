from __future__ import annotations

from django.contrib import admin, messages
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.views.decorators.http import require_GET, require_POST

from apps.dispatch.models import RobotDispatch
from apps.dispatch.services import trigger_dispatch_if_ready
from apps.notifications.services import broadcast_order_update
from apps.orders.models import Order

from .services import store


def _mock_order_id_for_backend_order(order: Order) -> str:
    return f"backend-order-{order.id}"


def _ensure_mock_order(order: Order) -> str:
    mock_order_id = _mock_order_id_for_backend_order(order)
    existing = store.get_order(mock_order_id)
    if existing:
        return mock_order_id

    store.create_order(
        {
            "id": mock_order_id,
            "extId": f"order-{order.id}",
            "robot": "",
            "clientName": order.student_name,
            "src": {"extId": f"vendor-{order.vendor_id}"},
            "dst": {"extId": f"dropoff-{order.id}"},
        }
    )
    return mock_order_id


def _dispatch_row(order: Order) -> dict:
    dispatch = getattr(order, "dispatch", None)
    mock_order_id = ""
    mock_status = "not_created"

    if dispatch and isinstance(dispatch.response_payload, dict):
        mock_order_id = dispatch.response_payload.get("mock_order_id", "")
    if mock_order_id:
        mock_order = store.get_order(mock_order_id)
        if mock_order:
            mock_status = mock_order["status"]

    return {
        "order_id": order.id,
        "student_name": order.student_name,
        "vendor_name": order.vendor.name,
        "pickup": order.vendor.location_label,
        "dropoff": order.delivery_location,
        "order_status": order.status,
        "dispatch_status": dispatch.status if dispatch else "",
        "mock_order_id": mock_order_id,
        "mock_status": mock_status,
        "next_vendor_action": _next_vendor_action(order.status),
        "updated_at": order.updated_at.isoformat(),
    }


def _next_vendor_action(status: str) -> dict[str, str] | None:
    action_map = {
        Order.Status.PLACED: {"target": Order.Status.ACCEPTED, "label": "Accept Order"},
        Order.Status.ACCEPTED: {"target": Order.Status.PREPARING, "label": "Start Preparing"},
        Order.Status.PREPARING: {"target": Order.Status.READY, "label": "Mark Ready"},
    }
    return action_map.get(status)


@require_GET
def robot_simulator_dashboard(request: HttpRequest):
    context = {
        **admin.site.each_context(request),
        "title": "Robot Simulator Dashboard",
        "simulator_state_url": reverse("admin:robot_simulator_state"),
        "simulator_set_status_url": reverse("admin:robot_simulator_set_status", args=[0, "READY"])
        .replace("/0/", "/ORDER_ID/")
        .replace("/READY/", "/TARGET_STATUS/"),
        "simulator_dispatch_url": reverse("admin:robot_simulator_dispatch", args=[0]).replace("/0/", "/ORDER_ID/"),
        "simulator_advance_url": reverse("admin:robot_simulator_advance", args=[0]).replace("/0/", "/ORDER_ID/"),
    }
    return TemplateResponse(request, "admin/robot_simulator.html", context)


@require_GET
def robot_simulator_state(_request: HttpRequest):
    orders = (
        Order.objects.select_related("vendor", "dispatch")
        .filter(
            status__in=[
                Order.Status.PLACED,
                Order.Status.ACCEPTED,
                Order.Status.PREPARING,
                Order.Status.READY,
                Order.Status.DISPATCHED,
                Order.Status.DELIVERED,
            ]
        )
        .order_by("-updated_at")[:100]
    )
    return JsonResponse({"orders": [_dispatch_row(order) for order in orders], "robots": store.robots()})


@require_POST
def robot_simulator_set_status(_request: HttpRequest, order_id: int, target_status: str):
    order = get_object_or_404(Order, pk=order_id)
    allowed = {Order.Status.ACCEPTED, Order.Status.PREPARING, Order.Status.READY}
    if target_status not in allowed:
        return JsonResponse({"detail": "Unsupported status transition target."}, status=400)

    order.status = target_status
    order.save(update_fields=["status", "updated_at"])
    broadcast_order_update(order)
    return JsonResponse({"ok": True, "status": target_status})


@require_POST
def robot_simulator_dispatch(request: HttpRequest, order_id: int):
    order = get_object_or_404(Order.objects.select_related("vendor"), pk=order_id)
    if order.status != Order.Status.READY:
        return JsonResponse({"detail": "Only READY orders can be dispatched."}, status=400)

    trigger_dispatch_if_ready(order)
    dispatch = getattr(order, "dispatch", None)
    if dispatch:
        payload = dict(dispatch.response_payload or {})
        payload["mock_order_id"] = _ensure_mock_order(order)
        dispatch.response_payload = payload
        dispatch.save(update_fields=["response_payload", "updated_at"])

    messages.success(request, f"Order #{order.id} dispatched to robot simulator.")
    return JsonResponse({"ok": True})


@require_POST
def robot_simulator_advance(request: HttpRequest, order_id: int):
    order = get_object_or_404(Order.objects.select_related("vendor"), pk=order_id)
    if order.status == Order.Status.READY:
        trigger_dispatch_if_ready(order)
        order.refresh_from_db()
    if order.status != Order.Status.DISPATCHED:
        return JsonResponse({"detail": "Order must be DISPATCHED before advancing delivery."}, status=400)

    dispatch = getattr(order, "dispatch", None)
    if not dispatch:
        dispatch = RobotDispatch.objects.create(
            order=order,
            provider=RobotDispatch.Provider.ROBOT,
            status=RobotDispatch.Status.SENT,
            request_payload={
                "order_id": order.id,
                "pickup_location": order.vendor.location_label,
                "dropoff_location": order.delivery_location,
            },
            response_payload={},
        )
    if not isinstance(dispatch.response_payload, dict):
        dispatch.response_payload = {}

    mock_order_id = dispatch.response_payload.get("mock_order_id") or _ensure_mock_order(order)
    dispatch.response_payload["mock_order_id"] = mock_order_id
    dispatch.save(update_fields=["response_payload", "updated_at"])
    mock_order = store.get_order(mock_order_id)
    if not mock_order:
        return JsonResponse({"detail": "Mock order not found in simulator."}, status=404)

    flow = ["accepted", "pickUp", "transporting", "dropOff", "completed"]
    current = mock_order["status"]
    if current not in flow:
        next_state = "accepted"
    elif current == "completed":
        next_state = "completed"
    else:
        next_state = flow[flow.index(current) + 1]

    updated = store.update_order_state(mock_order_id, next_state, ready=True)
    if updated and updated["status"] == "completed":
        order.status = Order.Status.DELIVERED
        order.save(update_fields=["status", "updated_at"])
        broadcast_order_update(order)

    return JsonResponse({"ok": True, "next_status": next_state})


_original_get_urls = admin.site.get_urls


def _simulator_urls():
    return [
        path("robot-simulator/", admin.site.admin_view(robot_simulator_dashboard), name="robot_simulator_dashboard"),
        path("robot-simulator/state/", admin.site.admin_view(robot_simulator_state), name="robot_simulator_state"),
        path(
            "robot-simulator/orders/<int:order_id>/status/<str:target_status>/",
            admin.site.admin_view(robot_simulator_set_status),
            name="robot_simulator_set_status",
        ),
        path(
            "robot-simulator/orders/<int:order_id>/dispatch/",
            admin.site.admin_view(robot_simulator_dispatch),
            name="robot_simulator_dispatch",
        ),
        path(
            "robot-simulator/orders/<int:order_id>/advance/",
            admin.site.admin_view(robot_simulator_advance),
            name="robot_simulator_advance",
        ),
    ]


def _patched_get_urls():
    return _simulator_urls() + _original_get_urls()


if not getattr(admin.site, "_robot_simulator_patched", False):
    admin.site.get_urls = _patched_get_urls
    # Stock `admin/index.html` is resolved before app templates; use AdminSite hook instead.
    admin.site.index_template = "admin/robot_simulator_admin_index.html"
    admin.site._robot_simulator_patched = True
