from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from vehicles.models import Vehicle

User = get_user_model()


class Booking(models.Model):
    """
    Booking model for car rental system
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.id} - {self.customer.username} - {self.vehicle.full_name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Check if start_date is in the future
        if self.start_date and self.start_date <= timezone.now():
            raise ValidationError("Start date must be in the future.")
        
        # Check if end_date is after start_date
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")
        
        # Check if vehicle is available for the booking period
        if self.vehicle and self.start_date and self.end_date:
            overlapping_bookings = Booking.objects.filter(
                vehicle=self.vehicle,
                status__in=['confirmed', 'active'],
                start_date__lt=self.end_date,
                end_date__gt=self.start_date
            )
            if self.pk:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)
            
            if overlapping_bookings.exists():
                raise ValidationError("Vehicle is not available for the selected dates.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def duration_days(self):
        """Calculate duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    @property
    def is_active(self):
        """Check if booking is currently active"""
        now = timezone.now()
        return (self.status == 'active' and 
                self.start_date <= now <= self.end_date)

    @property
    def is_overdue(self):
        """Check if booking is overdue"""
        now = timezone.now()
        return (self.status == 'active' and 
                self.end_date < now)
