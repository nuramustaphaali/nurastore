from django.urls import path
from .views import CreateReviewView, UserProfileDetailView, DeliveryZoneListView, OrderListView, OrderDetailView, PaymentVerifyView,CheckoutView, CartView, CartItemView, ProductListView, ProductDetailView, CategoryListView, RegisterView, UserProfileView, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    ProductListView, admin_dashboard_view, ProductDetailView, CategoryListView, 
    CreateReviewView, UserProfileDetailView # Ensure these are imported
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Auth Endpoints
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Default JWT Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('me/', UserProfileView.as_view(), name='auth_me'), 

    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/detail/<slug:slug>/', ProductDetailView.as_view(), name='product_detail_full'),    
    path('products/<int:product_id>/reviews/', CreateReviewView.as_view(), name='create_review'),
    path('profile/', UserProfileDetailView.as_view(), name='user_profile'),

    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('cart/', CartView.as_view(), name='cart_detail'),
    path('cart/items/<int:item_id>/', CartItemView.as_view(), name='cart_item_action'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/verify/', PaymentVerifyView.as_view(), name='payment_verify'),

    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:id>/', OrderDetailView.as_view(), name='order_detail'),
    path('dashboard-report/', admin_dashboard_view, name='admin_dashboard'),
    path('delivery-zones/', DeliveryZoneListView.as_view(), name='delivery_zones'),

    # 1. The Schema File (JSON)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # 2. Swagger UI (Interactive - Test your API here)
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # 3. Redoc (Professional Reading View)
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]