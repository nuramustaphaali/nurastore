from django.urls import path
from .views import DeliveryZoneListView, OrderListView, OrderDetailView, PaymentVerifyView,CheckoutView, CartView, CartItemView, ProductListView, ProductDetailView, CategoryListView, RegisterView, UserProfileView, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Auth Endpoints
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Default JWT Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('me/', UserProfileView.as_view(), name='auth_me'), 

    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('cart/', CartView.as_view(), name='cart_detail'),
    path('cart/items/<int:item_id>/', CartItemView.as_view(), name='cart_item_action'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/verify/', PaymentVerifyView.as_view(), name='payment_verify'),

    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:id>/', OrderDetailView.as_view(), name='order_detail'),

    path('delivery-zones/', DeliveryZoneListView.as_view(), name='delivery_zones'),
]