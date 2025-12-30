from django.urls import path
from .views import CheckoutView, CartView, CartItemView, ProductListView, ProductDetailView, CategoryListView, RegisterView, UserProfileView, LogoutView
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

]