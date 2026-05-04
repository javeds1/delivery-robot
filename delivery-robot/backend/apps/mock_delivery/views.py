from django.conf import settings
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    CreateInputSerializer,
    OrderStateSerializer,
    OrdersResponseSerializer,
    RobotsResponseSerializer,
    UIUserSerializer,
)
from .services import store

# JWT for kiosk/integration clients; Session for same-site browser sessions.
MOCK_AUTH = [JWTAuthentication, SessionAuthentication]


class RobotsView(APIView):
    authentication_classes = MOCK_AUTH
    permission_classes = [IsAuthenticated]

    def get(self, _request):
        payload = {"robots": store.robots()}
        serializer = RobotsResponseSerializer(payload)
        return Response(serializer.data)


class OrdersView(APIView):
    authentication_classes = MOCK_AUTH
    permission_classes = [IsAuthenticated]

    def get(self, request):
        robot = request.query_params.get("robot")
        only_active_raw = request.query_params.get("only_active")
        only_active = None
        if only_active_raw is not None:
            only_active = only_active_raw.lower() in {"true", "1", "yes"}
        payload = {"orders": store.list_orders(robot=robot, only_active=only_active)}
        serializer = OrdersResponseSerializer(payload)
        return Response(serializer.data)

    def post(self, request):
        if not settings.MOCK_DELIVERY_ENABLED:
            return Response(
                {"type": "about:blank", "title": "Service Unavailable", "status": 503, "detail": "Mock delivery endpoints are disabled."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        serializer = CreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = store.create_order(serializer.validated_data)
        return Response(OrderStateSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    authentication_classes = MOCK_AUTH
    permission_classes = [IsAuthenticated]

    def get(self, _request, order_id: str):
        order = store.get_order(order_id)
        if order is None:
            return Response(
                {"type": "about:blank", "title": "Not Found", "status": 404, "detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(OrderStateSerializer(order).data)


class OrderActionView(APIView):
    authentication_classes = MOCK_AUTH
    permission_classes = [IsAuthenticated]

    STATUS_MAP = {
        "cancel": ("canceled", None),
        "close": ("dropOffTransaction", None),
        "open": ("pickUpTransaction", None),
        "ready": ("accepted", True),
        "return-to-pickup": ("returnTransporting", None),
    }

    def post(self, _request, order_id: str, action: str):
        target = self.STATUS_MAP.get(action)
        if not target:
            return Response(
                {"type": "about:blank", "title": "Not Found", "status": 404, "detail": "Action not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        next_status, ready = target
        order = store.update_order_state(order_id=order_id, target_status=next_status, ready=ready)
        if order is None:
            return Response(
                {"type": "about:blank", "title": "Not Found", "status": 404, "detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(OrderStateSerializer(order).data)


class UserView(APIView):
    authentication_classes = MOCK_AUTH
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payload = store.user_payload(request.user)
        serializer = UIUserSerializer(payload)
        return Response(serializer.data)
