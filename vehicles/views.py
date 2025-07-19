from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from .models import Vehicle
from .serializers import VehicleSerializer, VehicleListSerializer


@extend_schema_view(
    get=extend_schema(
        tags=['Vehicles'],
        summary='List user vehicles',
        description='List user vehicles',
        responses={200: VehicleListSerializer}
    ),
    post=extend_schema(
        tags=['Vehicles'],
        summary='Create new vehicle',
        description='Add a new vehicle',
        request=VehicleSerializer,
        responses={
            201: VehicleSerializer,
            400: VehicleSerializer,
        }
    )
)
class VehicleListCreateView(generics.ListCreateAPIView):
    """
    List all vehicles owned by the authenticated user
    Create a new vehicle
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return VehicleListSerializer
        return VehicleSerializer
    
    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema_view(
    get=extend_schema(
        tags=['Vehicles'],
        summary='Get vehicle details',
        description='Get vehicle details',
        responses={200: VehicleSerializer}
    ),
    put=extend_schema(
        tags=['Vehicles'],
        summary='Update vehicle',
        description='Update vehicle',
        request=VehicleSerializer,
        responses={200: VehicleSerializer}
    ),
    patch=extend_schema(
        tags=['Vehicles'],
        summary='Partially update vehicle',
        description='Partially update vehicle',
        request=VehicleSerializer,
        responses={200: VehicleSerializer}
    ),
    delete=extend_schema(
        tags=['Vehicles'],
        summary='Delete vehicle',
        description='Delete vehicle',
        responses={204: None}
    )
)
class VehicleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a vehicle
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VehicleSerializer
    
    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user)
    
    def get_object(self):
        vehicle_id = self.kwargs.get('pk')
        return get_object_or_404(Vehicle, id=vehicle_id, owner=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        vehicle = self.get_object()
        vehicle.delete()
        return Response({
            'message': 'Vehicle deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
