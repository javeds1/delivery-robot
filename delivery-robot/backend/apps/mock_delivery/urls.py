from django.urls import path

from .views import OrderActionView, OrderDetailView, OrdersView, RobotsView, UserView


urlpatterns = [
    path("api/mock-delivery/orders", OrdersView.as_view(), name="mock_delivery_orders"),
    path("api/mock-delivery/orders/<str:order_id>", OrderDetailView.as_view(), name="mock_delivery_order_detail"),
    path("api/mock-delivery/orders/<str:order_id>/<str:action>", OrderActionView.as_view(), name="mock_delivery_order_action"),
    path("api/mock-delivery/robots", RobotsView.as_view(), name="mock_delivery_robots"),
    path("api/mock-delivery/user", UserView.as_view(), name="mock_delivery_user"),
]
