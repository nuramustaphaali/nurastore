from django.shortcuts import render

def index(request):
    """
    Renders the Single Page Application (SPA) shell.
    Data will be fetched via JS from the API later.
    """
    return render(request, 'web/index.html')

def login_view(request):
    return render(request, 'web/login.html')

def register_view(request):
    return render(request, 'web/register.html')

def checkout_view(request):
    return render(request, 'web/checkout.html')

def order_success_view(request):
    return render(request, 'web/order_success.html')

def orders_view(request):
    return render(request, 'web/orders.html')