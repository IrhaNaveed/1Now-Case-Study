from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for Vehicle model
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner', 'make', 'model', 'year', 'plate_number', 
            'fuel_type', 'transmission', 'daily_rate', 'status', 
            'description', 'mileage', 'color', 'seats', 'full_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def validate_plate_number(self, value):
        """
        Validate plate number uniqueness
        """
        if Vehicle.objects.filter(plate_number=value).exists():
            raise serializers.ValidationError("A vehicle with this plate number already exists.")
        return value

    def validate_daily_rate(self, value):
        """
        Validate daily rate is positive
        """
        if value <= 0:
            raise serializers.ValidationError("Daily rate must be greater than zero.")
        return value

    def validate_year(self, value):
        """
        Validate year is reasonable
        """
        if value < 1900 or value > 2025:
            raise serializers.ValidationError("Year must be between 1900 and 2025.")
        return value


class VehicleListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for vehicle listing
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner', 'make', 'model', 'year', 'plate_number',
            'fuel_type', 'transmission', 'daily_rate', 'status',
            'color', 'seats', 'full_name', 'created_at'
        ] 