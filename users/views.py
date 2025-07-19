from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer

User = get_user_model()


@extend_schema(
    tags=['Authentication'],
    summary='Register a new user',
    description='Create a new user account',
    request=UserRegistrationSerializer,
    responses={
        201: UserRegistrationSerializer,
        400: UserRegistrationSerializer,
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='User login',
    description='Login user and return JWT token',
    request=UserLoginSerializer,
    responses={
        200: UserLoginSerializer,
        400: UserLoginSerializer,
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user and return JWT token
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        tags=['Authentication'],
        summary='Get user profile',
        description='Get user profile',
        responses={200: UserProfileSerializer}
    ),
    put=extend_schema(
        tags=['Authentication'],
        summary='Update user profile',
        description='Update user profile',
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer}
    ),
    patch=extend_schema(
        tags=['Authentication'],
        summary='Partially update user profile',
        description='Partially update user profile',
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer}
    )
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
