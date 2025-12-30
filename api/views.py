from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from core.email_service import EmailService 

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
    Returns a list of all available products.
    """
    queryset = Product.objects.filter(is_available=True).order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny] # Public access

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