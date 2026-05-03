from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase


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
