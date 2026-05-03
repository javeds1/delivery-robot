from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase

from apps.orders.models import Order
from apps.vendors.models import Vendor


class MockDeliveryApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="mock_delivery_vendor",
            email="vendor@example.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)

    @override_settings(MOCK_DELIVERY_ENABLED=True, MOCK_DELIVERY_STATE_MODE="deterministic")
    def test_create_and_fetch_order(self):
        create_response = self.client.post(
            "/api/mock-delivery/orders",
            {
                "id": "ddf6f55b-e8e7-463a-bf71-0fa33711d833",
                "extId": "order-1001",
                "src": {"lat": 30.3414, "lon": -97.6768, "address": "North Hall"},
                "dst": {"lat": 30.3422, "lon": -97.6759, "address": "Engineering Building"},
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        order_id = create_response.data["id"]
        self.assertEqual(create_response.data["status"], "new")

        fetch_response = self.client.get(f"/api/mock-delivery/orders/{order_id}")
        self.assertEqual(fetch_response.status_code, 200)
        self.assertEqual(fetch_response.data["extId"], "order-1001")

    @override_settings(MOCK_DELIVERY_ENABLED=False)
    def test_order_creation_disabled_with_flag(self):
        response = self.client.post(
            "/api/mock-delivery/orders",
            {
                "id": "11111111-e8e7-463a-bf71-0fa33711d833",
                "dst": {"lat": 30.34, "lon": -97.67, "address": "Library"},
            },
            format="json",
        )
        self.assertEqual(response.status_code, 503)

    def test_list_robots(self):
        response = self.client.get("/api/mock-delivery/robots")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data["robots"]), 1)

    @override_settings(MOCK_DELIVERY_ENABLED=True)
    def test_cancel_order(self):
        create_response = self.client.post(
            "/api/mock-delivery/orders",
            {
                "id": "22222222-e8e7-463a-bf71-0fa33711d833",
                "dst": {"lat": 30.34, "lon": -97.67, "address": "Lab B"},
            },
            format="json",
        )
        order_id = create_response.data["id"]

        cancel_response = self.client.post(f"/api/mock-delivery/orders/{order_id}/cancel")
        self.assertEqual(cancel_response.status_code, 200)
        self.assertEqual(cancel_response.data["status"], "canceled")


class RobotSimulatorAdminTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123",
        )
        self.vendor_user = user_model.objects.create_user(
            username="vendor_manager",
            email="vendor@example.com",
            password="password123",
        )
        self.vendor = Vendor.objects.create(
            name="Cafe A",
            location_label="Cafe Pickup",
            manager=self.vendor_user,
        )
        self.order = Order.objects.create(
            vendor=self.vendor,
            student_name="Student Test",
            phone="555-0100",
            delivery_location="Dorm 7",
            status=Order.Status.PLACED,
        )
        self.client.login(username="admin", password="password123")

    def test_simulator_dashboard_loads(self):
        response = self.client.get("/admin/robot-simulator/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Robot Simulator Dashboard")

    def test_dispatch_then_advance_to_complete(self):
        self.client.post(f"/admin/robot-simulator/orders/{self.order.id}/status/ACCEPTED/")
        self.client.post(f"/admin/robot-simulator/orders/{self.order.id}/status/PREPARING/")
        self.client.post(f"/admin/robot-simulator/orders/{self.order.id}/status/READY/")

        dispatch_response = self.client.post(f"/admin/robot-simulator/orders/{self.order.id}/dispatch/")
        self.assertEqual(dispatch_response.status_code, 200)

        for _ in range(5):
            advance_response = self.client.post(f"/admin/robot-simulator/orders/{self.order.id}/advance/")
            self.assertEqual(advance_response.status_code, 200)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.DELIVERED)

    def test_vendor_status_step_actions(self):
        response = self.client.post(f"/admin/robot-simulator/orders/{self.order.id}/status/ACCEPTED/")
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.ACCEPTED)
