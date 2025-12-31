from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from core.email_service import EmailService 
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db import transaction
from .models import Order, OrderItem, Cart

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import OrderSerializer, ProductSerializer, CategorySerializer


from django.shortcuts import get_object_or_404
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Product
from .serializers import CartSerializer

from core.paystack import Paystack
from django.shortcuts import render

from .models import Review
from .serializers import ReviewSerializer, ProductDetailSerializer

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        # 1. Save the user
        user = serializer.save()
        
        # 2. Trigger the Email Event (Background)
        EmailService.send_welcome_email(user)

class UserProfileView(views.APIView):
    """
    Get the current logged-in user's details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# Helper view to blacklist token on logout (Optional for basic JWT, but good practice)
class LogoutView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)



class ProductListView(generics.ListAPIView):
    """
    Returns a list of products with support for:
    - Search: ?search=iphone
    - Filtering: ?category=electronics&price_min=1000
    - Ordering: ?ordering=price (or -price for high to low)
    """
    # Optimized query: select_related reduces database hits for categories
    queryset = Product.objects.filter(is_available=True).select_related('category').order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    # Enable the Filter Backends
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    
    # 1. Search Fields (checks name and description)
    search_fields = ['name', 'description', 'category__name']
    
    # 2. Filter Fields (Exact matches)
    filterset_fields = {
        'category': ['exact'],      # ?category=1
        'price': ['gte', 'lte'],    # ?price__gte=1000 (Greater than or equal)
    }
    
    # 3. Ordering Fields
    ordering_fields = ['price', 'created_at', 'name']

    @method_decorator(cache_page(60 * 15)) 
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @extend_schema(
        summary="List & Filter Products",
        description="Get a paginated list of products. Use query params to filter by category, search text, or sort by price.",
        parameters=[
            OpenApiParameter(name='search', description='Search term for product name', required=False, type=str),
            OpenApiParameter(name='category', description='Category ID to filter by', required=False, type=int),
            OpenApiParameter(name='ordering', description='Sort by: price, -price, created_at', required=False, type=str),
        ],
        tags=['Storefront'] # Groups this endpoint under a nice label
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# class ProductDetailView(generics.RetrieveAPIView):
#     """
#     Returns details of a single product by slug.
#     """
#     queryset = Product.objects.filter(is_available=True)
#     serializer_class = ProductSerializer
#     permission_classes = [AllowAny]
#     lookup_field = 'slug'

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]




class CartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get or Create cart for user
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        """ Add item to cart """
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)

        # Logic: If item exists, update quantity. Else create new.
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Return updated cart
        return Response(CartSerializer(cart).data)

class CartItemView(views.APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        """ Update quantity (e.g., + or - buttons) """
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.data.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete() # Remove if 0

        return Response(CartSerializer(cart_item.cart).data)

    def delete(self, request, item_id):
        """ Remove item completely """
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart = cart_item.cart
        cart_item.delete()
        return Response(CartSerializer(cart).data)




class CheckoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Get User's Cart
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": "No cart found"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Extract Shipping Data
        data = request.data
        
        # 3. Database Transaction (All or Nothing)
        try:
            with transaction.atomic():
                # A. Create Order Shell
                order = Order.objects.create(
                    user=request.user,
                    full_name=data.get('full_name'),
                    address=data.get('address'),
                    city=data.get('city'),
                    state=data.get('state'),
                    phone=data.get('phone'),
                    total_amount=cart.total_price # Calculated server-side from cart model
                )

                # B. Move Items & Deduct Stock
                items_to_create = []
                for item in cart.items.select_related('product'):
                    product = item.product
                    
                    # Stock Check
                    if product.stock < item.quantity:
                        raise ValueError(f"Not enough stock for {product.name}")

                    # Deduct Stock
                    product.stock -= item.quantity
                    product.save()

                    # Create Immutable Order Item
                    items_to_create.append(OrderItem(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price, # Snapshot current price
                        quantity=item.quantity
                    ))

                # Bulk Create for performance
                OrderItem.objects.bulk_create(items_to_create)

                # C. Clear Cart
                cart.items.all().delete()
                
                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Checkout failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentVerifyView(views.APIView):
    """
    Called by Frontend after Paystack redirect return.
    """
    permission_classes = [AllowAny] # Public, because Paystack/Browser calls it

    def get(self, request):
        reference = request.query_params.get('reference')
        if not reference:
            return Response({"error": "No reference provided"}, status=400)

        paystack = Paystack()
        res = paystack.verify_transaction(reference)

        if res['status']:
            # Find order and mark as paid
            try:
                order = Order.objects.get(payment_reference=reference)
                order.is_paid = True
                order.status = 'paid'
                order.save()
                return Response({"status": "success", "message": "Payment verified"})
            except Order.DoesNotExist:
                return Response({"error": "Order not found"}, status=404)
        
        return Response({"status": "failed", "message": "Payment verification failed"}, status=400)       

from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Models
from .models import Product, Cart, Order, OrderItem
from core.models import DeliveryZone # Imported for Delivery Logic
from core.paystack import Paystack
from .serializers import OrderSerializer

class CheckoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Get User's Cart
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": "No cart found"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Extract Data
        data = request.data
        payment_method = data.get('payment_method', 'paystack')
        state_name = data.get('state')

        # 3. CALCULATE DELIVERY FEE (Server-Side Validation)
        # We don't trust the frontend price. We verify it here.
        delivery_fee = 0
        try:
            # Case-insensitive match for state (e.g. "kano" matches "Kano")
            zone = DeliveryZone.objects.get(state__iexact=state_name)
            delivery_fee = zone.fee
        except DeliveryZone.DoesNotExist:
            # Fallback/Default fee if state is not in your DB
            delivery_fee = 2500 # Default Standard Delivery

        # 4. Start Database Transaction
        try:
            with transaction.atomic():
                
                # Calculate Grand Total (Cart Subtotal + Delivery Fee)
                grand_total = cart.total_price + delivery_fee

                # A. Create the Order
                order = Order.objects.create(
                    user=request.user,
                    full_name=data.get('full_name'),
                    address=data.get('address'),
                    city=data.get('city'),
                    state=state_name,
                    phone=data.get('phone'),
                    delivery_fee=delivery_fee, # Save the fee
                    total_amount=grand_total,  # Save the final total
                    payment_method=payment_method
                )

                # B. Move Items & Deduct Stock
                items_to_create = []
                for item in cart.items.select_related('product'):
                    product = item.product
                    
                    # Check Stock
                    if product.stock < item.quantity:
                        raise ValueError(f"Not enough stock for {product.name}")

                    # Deduct Stock
                    product.stock -= item.quantity
                    product.save()

                    # Create Order Item (Snapshot of price/name)
                    items_to_create.append(OrderItem(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price,
                        quantity=item.quantity
                    ))

                # Bulk Create for performance
                OrderItem.objects.bulk_create(items_to_create)

                # C. Clear the Cart
                cart.items.all().delete()
                
                # --- D. PAYMENT PROCESSING ---
                
                # Option A: Paystack (Card/Transfer)
                if payment_method == 'paystack':
                    paystack = Paystack()
                    # Initialize transaction with the Grand Total (Cart + Delivery)
                    res = paystack.initialize_transaction(
                        email=request.user.email,
                        amount=order.total_amount,
                        order_id=order.id
                    )
                    
                    if res['status']:
                        # Save the Paystack Reference
                        order.payment_reference = res['reference']
                        order.save()
                        
                        return Response({
                            "message": "Order created. Redirecting to payment.",
                            "payment_url": res['auth_url'],
                            "type": "paystack"
                        }, status=status.HTTP_201_CREATED)
                    else:
                        raise ValueError("Paystack initialization failed.")

                # Option B: Payment on Delivery (POD) / Bank Transfer
                else:
                    return Response({
                        "message": "Order placed successfully!",
                        "type": "pod"
                    }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderListView(generics.ListAPIView):
    """ List all orders for the logged-in user """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(generics.RetrieveAPIView):
    """ View specific order details """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Ensure user can only see their OWN orders
        return Order.objects.filter(user=self.request.user)

# ... imports ...
from core.models import DeliveryZone # Import the new model

class DeliveryZoneListView(views.APIView):
    permission_classes = [AllowAny] # Public info

    def get(self, request):
        zones = DeliveryZone.objects.filter(is_active=True).values('id', 'state', 'fee', 'estimated_time')
        return Response(list(zones))


# A. Product Detail (Single Page)
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

# B. Create Review (With Verification Logic)
class CreateReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        user = self.request.user

        # 1. Prevent Duplicates
        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError("You have already reviewed this product.")

        # 2. Check for Verified Purchase
        # We check if this user has any DELIVERED order containing this product
        has_purchased = OrderItem.objects.filter(
            order__user=user, 
            order__status='delivered', 
            product=product
        ).exists()

        serializer.save(user=user, product=product, is_verified_purchase=has_purchased)

# C. User Profile (Get & Update)
class UserProfileDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile
        return Response({
            "username": user.username,
            "email": user.email,
            "phone": profile.phone,
            "address": profile.address,
            "city": profile.city,
            "state": profile.state
        })

    def put(self, request):
        user = request.user
        data = request.data
        
        # Update Profile Fields
        user.profile.phone = data.get('phone', user.profile.phone)
        user.profile.address = data.get('address', user.profile.address)
        user.profile.city = data.get('city', user.profile.city)
        user.profile.state = data.get('state', user.profile.state)
        user.profile.save()
        
        return Response({"message": "Profile updated successfully"})


from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count

# ... existing imports ...

@staff_member_required
def admin_dashboard_view(request):
    """
    Custom Dashboard for Business Owners.
    """
    # 1. Financials
    total_revenue = Order.objects.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # 2. Inventory Health
    low_stock_count = Product.objects.filter(stock__lt=10).count()
    
    # 3. Recent Activity
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    
    # 4. Top Products (Simple Logic: Filter by available)
    # In a real app, you'd aggregate OrderItems, but for now we list available stock
    top_products = Product.objects.order_by('-created_at')[:5]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'low_stock_count': low_stock_count,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'title': 'Business Dashboard' # Required for Admin template
    }
    
    return render(request, 'admin/sales_dashboard.html', context)