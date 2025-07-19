from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_date
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from .models import Booking
from .serializers import BookingSerializer, BookingListSerializer


@extend_schema_view(
    get=extend_schema(
        tags=['Bookings'],
        summary='List user bookings',
        description='List user bookings',
        parameters=[
            OpenApiParameter(name='status', description='Filter by status', required=False, type=str),
            OpenApiParameter(name='vehicle', description='Filter by vehicle', required=False, type=int),
            OpenApiParameter(name='from', description='Filter from date', required=False, type=str),
            OpenApiParameter(name='to', description='Filter to date', required=False, type=str),
        ],
        responses={200: BookingListSerializer}
    ),
    post=extend_schema(
        tags=['Bookings'],
        summary='Create new booking',
        description='Create a new booking',
        request=BookingSerializer,
        responses={
            201: BookingSerializer,
            400: BookingSerializer,
        }
    )
)
class BookingListCreateView(generics.ListCreateAPIView):
    """
    List all bookings for the authenticated user
    Create a new booking
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'vehicle']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BookingListSerializer
        return BookingSerializer
    
    def get_queryset(self):
        queryset = Booking.objects.filter(customer=self.request.user)
        
        # Add date filtering
        from_date = self.request.query_params.get('from', None)
        to_date = self.request.query_params.get('to', None)
        
        if from_date:
            from_date = parse_date(from_date)
            if from_date:
                queryset = queryset.filter(start_date__date__gte=from_date)
        
        if to_date:
            to_date = parse_date(to_date)
            if to_date:
                queryset = queryset.filter(end_date__date__lte=to_date)
        
        return queryset
    
    def perform_create(self, serializer):
        booking = serializer.save()
        
        # Update vehicle status to rented if booking is confirmed
        if booking.status == 'confirmed':
            booking.vehicle.status = 'rented'
            booking.vehicle.save()


@extend_schema_view(
    get=extend_schema(
        tags=['Bookings'],
        summary='Get booking details',
        description='Get booking details',
        responses={200: BookingSerializer}
    ),
    put=extend_schema(
        tags=['Bookings'],
        summary='Update booking',
        description='Update booking',
        request=BookingSerializer,
        responses={200: BookingSerializer}
    ),
    patch=extend_schema(
        tags=['Bookings'],
        summary='Partially update booking',
        description='Partially update booking',
        request=BookingSerializer,
        responses={200: BookingSerializer}
    ),
    delete=extend_schema(
        tags=['Bookings'],
        summary='Cancel booking',
        description='Cancel booking',
        responses={204: None}
    )
)
class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a booking
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        return Booking.objects.filter(customer=self.request.user)
    
    def perform_update(self, serializer):
        booking = serializer.save()
        
        # Update vehicle status based on booking status
        if booking.status == 'cancelled':
            booking.vehicle.status = 'available'
            booking.vehicle.save()
        elif booking.status == 'confirmed':
            booking.vehicle.status = 'rented'
            booking.vehicle.save()
    
    def perform_destroy(self, instance):
        # Update vehicle status to available when booking is deleted
        instance.vehicle.status = 'available'
        instance.vehicle.save()
        instance.delete()
        
        return Response({
            'message': 'Booking cancelled successfully'
        }, status=status.HTTP_204_NO_CONTENT)
