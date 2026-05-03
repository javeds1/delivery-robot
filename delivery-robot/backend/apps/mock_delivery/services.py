from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import Any

from django.conf import settings
from django.utils import timezone


@dataclass
class MockOrder:
    id: str
    ext_id: str | None
    robot_name: str
    status: str
    src: dict[str, Any]
    dst: dict[str, Any]
    request: dict[str, Any]
    created_at: str
    scheduled_pick_up: str
    ready: bool

    def to_dict(self) -> dict[str, Any]:
        created_at_dt = datetime.fromisoformat(self.created_at)
        scheduled_pickup_dt = datetime.fromisoformat(self.scheduled_pick_up)
        robot = get_robot_state(self.robot_name)
        return {
            "id": self.id,
            "extId": self.ext_id,
            "src": self.src,
            "dst": self.dst,
            "scheduledPickUp": self.scheduled_pick_up,
            "request": self.request,
            "createdAt": self.created_at,
            "status": self.status,
            "ready": self.ready,
            "eta": {
                "pickUp": scheduled_pickup_dt.isoformat(),
                "dropOff": (scheduled_pickup_dt + timezone.timedelta(minutes=12)).isoformat(),
                "return": (scheduled_pickup_dt + timezone.timedelta(minutes=20)).isoformat(),
            },
            "robots": [robot] if robot else [],
        }


ROBOT_FLEET = [
    {
        "name": "robot-1",
        "position": {"lat": 30.3414, "lon": -97.6768, "yaw": 90.0},
        "route": [{"lat": 30.3414, "lon": -97.6768}, {"lat": 30.3422, "lon": -97.6759}],
        "deliveringOtherOrders": False,
    },
    {
        "name": "robot-2",
        "position": {"lat": 30.3408, "lon": -97.6772, "yaw": -23.4},
        "route": [{"lat": 30.3408, "lon": -97.6772}],
        "deliveringOtherOrders": True,
    },
]

ORDER_STATES = (
    "new",
    "accepted",
    "pickUp",
    "pickUpTransaction",
    "transporting",
    "dropOff",
    "dropOffTransaction",
    "completed",
    "returnTransporting",
    "returnTransaction",
    "returnDropOff",
    "returnCompleted",
    "canceled",
)
TIMED_TRANSITIONS = (
    ("new", 0),
    ("accepted", 30),
    ("pickUp", 90),
    ("transporting", 180),
    ("completed", 300),
)


def get_robot_state(robot_name: str) -> dict[str, Any] | None:
    for robot in ROBOT_FLEET:
        if robot["name"] == robot_name:
            return robot
    return None


class InMemoryOrderStore:
    def __init__(self) -> None:
        self._orders: dict[str, MockOrder] = {}
        self._lock = Lock()

    def create_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = timezone.now()
        order = MockOrder(
            id=payload["id"],
            ext_id=payload.get("extId"),
            robot_name=payload.get("robot") or self._next_available_robot(),
            status="new",
            src=self._to_order_point(payload.get("src")),
            dst=self._to_order_point(payload["dst"]),
            request=self._to_request(payload),
            created_at=now.isoformat(),
            scheduled_pick_up=(payload.get("scheduledPickUp") or now).isoformat(),
            ready=False,
        )
        with self._lock:
            self._orders[order.id] = order
        return order.to_dict()

    def list_orders(self, robot: str | None = None, only_active: bool | None = None) -> list[dict[str, Any]]:
        with self._lock:
            orders = [self._resolve_state(order).to_dict() for order in self._orders.values()]
        if robot:
            orders = [order for order in orders if any(item["name"] == robot for item in order["robots"])]
        if only_active:
            orders = [order for order in orders if order["status"] not in {"completed", "canceled"}]
        return sorted(orders, key=lambda order: order["createdAt"], reverse=True)

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        with self._lock:
            order = self._orders.get(order_id)
            if order is None:
                return None
            return self._resolve_state(order).to_dict()

    def update_order_state(self, order_id: str, target_status: str, ready: bool | None = None) -> dict[str, Any] | None:
        with self._lock:
            order = self._orders.get(order_id)
            if order is None:
                return None
            order.status = target_status
            if ready is not None:
                order.ready = ready
            return order.to_dict()

    def robots(self) -> list[dict[str, Any]]:
        return ROBOT_FLEET

    def user_payload(self, user) -> dict[str, Any]:
        return {
            "firstName": getattr(user, "first_name", None) or None,
            "lastName": getattr(user, "last_name", None) or None,
            "login": user.username,
            "email": user.email or "",
            "roles": [getattr(user, "role", "vendor")],
            "partnerId": "mock-partner",
            "features": {
                "adminOperations": True,
                "basicOperations": True,
                "cancelOrder": True,
                "createOrder": True,
                "dropOffOrder": True,
                "loadOrder": True,
                "manageOrder": True,
                "returnToPickUp": True,
                "viewOrder": True,
                "viewRobots": True,
            },
            "config": {
                "dispatchRadius": 10.0,
                "countryCode": "US",
                "omitPhone": False,
                "newOrderSound": True,
                "predefinedOrders": [],
            },
        }

    def _next_available_robot(self) -> str:
        for robot in ROBOT_FLEET:
            if not robot["deliveringOtherOrders"]:
                return robot["name"]
        return ROBOT_FLEET[0]["name"]

    def _resolve_state(self, order: MockOrder) -> MockOrder:
        if order.status == "canceled" or settings.MOCK_DELIVERY_STATE_MODE != "timed":
            return order

        created_at = datetime.fromisoformat(order.created_at)
        elapsed_seconds = int((timezone.now() - created_at).total_seconds())
        latest_status = order.status
        for status, threshold in TIMED_TRANSITIONS:
            if elapsed_seconds >= threshold:
                latest_status = status

        if latest_status != order.status:
            order.status = latest_status
        return order

    def _to_order_point(self, point: dict[str, Any] | None) -> dict[str, Any]:
        if not point:
            return {"lat": 30.3414, "lon": -97.6768, "address": "", "extId": ""}
        if "extId" in point:
            return {"lat": 30.3414, "lon": -97.6768, "address": "", "extId": point["extId"]}
        return {
            "lat": point["lat"],
            "lon": point["lon"],
            "address": point.get("address", ""),
            "extId": point.get("extId", ""),
        }

    def _to_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "src": {"address": self._to_order_point(payload.get("src")).get("address", "")},
            "dst": {"address": self._to_order_point(payload["dst"]).get("address", "")},
            "clientName": payload.get("clientName", ""),
        }


store = InMemoryOrderStore()
