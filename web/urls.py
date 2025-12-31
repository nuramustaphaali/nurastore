from django.urls import path
from . import views
from django.shortcuts import render

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/verify/', lambda r: render(r, 'web/verify_payment.html'), name='verify_ui'),
    path('order-success/', views.order_success_view, name='order_success'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/<int:id>/', lambda r, id: render(r, 'web/order_detail.html'), name='order_detail_ui'),
    path('product/<slug:slug>/', lambda r, slug: render(r, 'web/product_detail.html'), name='product_ui'),
    path('profile/', lambda r: render(r, 'web/profile.html'), name='profile_ui'),
    path('about/', views.about_view, name='about'),
    path('faq/', views.faq_view, name='faq'),
    path('contact/', views.contact_view, name='contact'),
]