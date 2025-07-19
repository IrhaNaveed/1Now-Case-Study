from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Booking
from vehicles.models import Vehicle


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model
    """
    customer = serializers.ReadOnlyField(source='customer.username')
    vehicle_details = serializers.SerializerMethodField()
    duration_days = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'vehicle', 'vehicle_details', 'start_date', 'end_date',
            'total_amount', 'status', 'deposit_amount', 'deposit_paid', 'notes',
            'duration_days', 'is_active', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer', 'total_amount', 'created_at', 'updated_at']

    def get_vehicle_details(self, obj):
        """Get vehicle details for the booking"""
        if obj.vehicle:
            return {
                'id': obj.vehicle.id,
                'make': obj.vehicle.make,
                'model': obj.vehicle.model,
                'year': obj.vehicle.year,
                'plate_number': obj.vehicle.plate_number,
                'daily_rate': obj.vehicle.daily_rate,
                'full_name': obj.vehicle.full_name
            }
        return None

    def validate(self, attrs):
        """Validate booking data"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        vehicle = attrs.get('vehicle')

        # Check if start_date is in the future
        if start_date and start_date <= timezone.now():
            raise serializers.ValidationError("Start date must be in the future.")

        # Check if end_date is after start_date
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError("End date must be after start date.")

        # Check if vehicle exists and is available
        if vehicle:
            if vehicle.status != 'available':
                raise serializers.ValidationError("Vehicle is not available for booking.")

            # Check for overlapping bookings
            if start_date and end_date:
                overlapping_bookings = Booking.objects.filter(
                    vehicle=vehicle,
                    status__in=['confirmed', 'active'],
                    start_date__lt=end_date,
                    end_date__gt=start_date
                )
                if self.instance:
                    overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
                
                if overlapping_bookings.exists():
                    raise serializers.ValidationError("Vehicle is not available for the selected dates.")

        return attrs

    def create(self, validated_data):
        """Create booking with calculated total amount"""
        vehicle = validated_data['vehicle']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        
        # Calculate duration and total amount
        duration = (end_date - start_date).days
        if duration == 0:
            duration = 1  # Minimum 1 day
        
        total_amount = vehicle.daily_rate * duration
        
        # Set deposit amount (20% of total)
        deposit_amount = total_amount * 0.2
        
        booking = Booking.objects.create(
            customer=self.context['request'].user,
            total_amount=total_amount,
            deposit_amount=deposit_amount,
            **validated_data
        )
        
        return booking


class BookingListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for booking listing
    """
    customer = serializers.ReadOnlyField(source='customer.username')
    vehicle_name = serializers.ReadOnlyField(source='vehicle.full_name')
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'vehicle', 'vehicle_name', 'start_date', 'end_date',
            'total_amount', 'status', 'duration_days', 'created_at'
        ] 