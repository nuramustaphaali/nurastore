from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from core.email_service import EmailService 


from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

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

class ProductDetailView(generics.RetrieveAPIView):
    """
    Returns details of a single product by slug.
    """
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]