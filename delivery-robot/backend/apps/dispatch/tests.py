from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.orders.models import Order
from apps.vendors.models import Vendor

from .models import RobotDispatch
from .services import trigger_dispatch_if_ready


class DispatchProviderRoutingTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="dispatch_user",
            email="dispatch@example.com",
            password="password123",
        )
        self.vendor = Vendor.objects.create(
            name="Test Vendor",
            location_label="Kitchen A",
            manager=self.user,
        )

    @patch("apps.dispatch.services.broadcast_order_update")
    @override_settings(DISPATCH_PROVIDER="mock", MOCK_DELIVERY_ENABLED=True)
    def test_ready_order_uses_mock_provider(self, _broadcast_order_update):
        order = Order.objects.create(
            vendor=self.vendor,
            student=self.user,
            student_name="Student One",
            phone="1234567890",
            delivery_location="Building 2",
            status=Order.Status.READY,
        )

        trigger_dispatch_if_ready(order)

        dispatch = RobotDispatch.objects.get(order=order)
        order.refresh_from_db()
        self.assertEqual(dispatch.provider, RobotDispatch.Provider.ROBOT)
        self.assertEqual(dispatch.status, RobotDispatch.Status.SENT)
        self.assertEqual(order.status, Order.Status.DISPATCHED)
        self.assertIn("mock_delivery_enabled", dispatch.response_payload)

    @patch("apps.dispatch.services.broadcast_order_update")
    @override_settings(DISPATCH_PROVIDER="real")
    def test_ready_order_can_switch_to_real_provider(self, _broadcast_order_update):
        order = Order.objects.create(
            vendor=self.vendor,
            student=self.user,
            student_name="Student Two",
            phone="1234567890",
            delivery_location="Building 3",
            status=Order.Status.READY,
        )

        trigger_dispatch_if_ready(order)

        dispatch = RobotDispatch.objects.get(order=order)
        self.assertEqual(dispatch.provider, RobotDispatch.Provider.FALLBACK)
        self.assertEqual(dispatch.status, RobotDispatch.Status.SENT)

    @patch("apps.dispatch.services.broadcast_order_update")
    def test_non_ready_order_is_not_dispatched(self, _broadcast_order_update):
        order = Order.objects.create(
            vendor=self.vendor,
            student=self.user,
            student_name="Student Three",
            phone="1234567890",
            delivery_location="Building 4",
            status=Order.Status.PREPARING,
        )

        trigger_dispatch_if_ready(order)

        self.assertFalse(RobotDispatch.objects.filter(order=order).exists())
