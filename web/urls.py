from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/verify/', lambda r: render(r, 'web/verify_payment.html'), name='verify_ui'),
    path('order-success/', views.order_success_view, name='order_success'),
    path('orders/', views.orders_view, name='orders'),
]