from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Booking
from vehicles.models import Vehicle

User = get_user_model()


class BookingModelTest(TestCase):
    """Test cases for Booking model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            make='Toyota',
            model='Camry',
            year=2020,
            plate_number='ABC123',
            daily_rate=50.00
        )
        self.start_date = timezone.now() + timedelta(days=1)
        self.end_date = timezone.now() + timedelta(days=3)
        
    def test_create_booking(self):
        """Test creating a new booking"""
        booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00
        )
        self.assertEqual(booking.customer, self.user)
        self.assertEqual(booking.vehicle, self.vehicle)
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.duration_days, 2)
    
    def test_booking_str_representation(self):
        """Test booking string representation"""
        booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00
        )
        expected = f"Booking {booking.id} - testuser - 2020 Toyota Camry"
        self.assertEqual(str(booking), expected)
    
    def test_booking_duration_calculation(self):
        """Test booking duration calculation"""
        booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00
        )
        self.assertEqual(booking.duration_days, 2)
    
    def test_booking_status_choices(self):
        """Test booking status choices"""
        booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00
        )
        self.assertIn(booking.status, dict(Booking.STATUS_CHOICES))


class BookingAPITest(APITestCase):
    """Test cases for Booking API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            make='Toyota',
            model='Camry',
            year=2020,
            plate_number='ABC123',
            daily_rate=50.00
        )
        self.start_date = timezone.now() + timedelta(days=1)
        self.end_date = timezone.now() + timedelta(days=3)
        
        self.client.force_authenticate(user=self.user)
        self.booking_list_url = reverse('bookings:booking-list-create')
    
    def test_create_booking(self):
        """Test creating a new booking"""
        data = {
            'vehicle': self.vehicle.id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'notes': 'Test booking'
        }
        response = self.client.post(self.booking_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer'], 'testuser')
        self.assertEqual(response.data['total_amount'], '100.00')  # 2 days * 50.00
        self.assertEqual(response.data['deposit_amount'], '20.00')  # 20% of total
    
    def test_create_booking_with_past_date(self):
        """Test creating booking with past start date"""
        past_date = timezone.now() - timedelta(days=1)
        data = {
            'vehicle': self.vehicle.id,
            'start_date': past_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }
        response = self.client.post(self.booking_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data)
    
    def test_create_booking_with_invalid_dates(self):
        """Test creating booking with end date before start date"""
        data = {
            'vehicle': self.vehicle.id,
            'start_date': self.end_date.isoformat(),
            'end_date': self.start_date.isoformat()
        }
        response = self.client.post(self.booking_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_date', response.data)
    
    def test_create_booking_with_unavailable_vehicle(self):
        """Test creating booking with unavailable vehicle"""
        self.vehicle.status = 'maintenance'
        self.vehicle.save()
        
        data = {
            'vehicle': self.vehicle.id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }
        response = self.client.post(self.booking_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('vehicle', response.data)
    
    def test_create_overlapping_booking(self):
        """Test creating overlapping booking"""
        # Create first booking
        first_booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00,
            status='confirmed'
        )
        
        # Try to create overlapping booking
        overlap_start = self.start_date + timedelta(hours=12)
        overlap_end = self.end_date + timedelta(hours=12)
        
        data = {
            'vehicle': self.vehicle.id,
            'start_date': overlap_start.isoformat(),
            'end_date': overlap_end.isoformat()
        }
        response = self.client.post(self.booking_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('vehicle', response.data)
    
    def test_list_bookings(self):
        """Test listing user's bookings"""
        booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00
        )
        
        response = self.client.get(self.booking_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['vehicle_name'], '2020 Toyota Camry')
    
    def test_list_bookings_with_filters(self):
        """Test listing bookings with filters"""
        booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00,
            status='confirmed'
        )
        
        # Filter by status
        response = self.client.get(f"{self.booking_list_url}?status=confirmed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Filter by vehicle
        response = self.client.get(f"{self.booking_list_url}?vehicle={self.vehicle.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_retrieve_booking(self):
        """Test retrieving a specific booking"""
        booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00
        )
        
        booking_detail_url = reverse('bookings:booking-detail', args=[booking.id])
        response = self.client.get(booking_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['customer'], 'testuser')
        self.assertEqual(response.data['total_amount'], '100.00')
    
    def test_update_booking_status(self):
        """Test updating booking status"""
        booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00
        )
        
        booking_detail_url = reverse('bookings:booking-detail', args=[booking.id])
        data = {'status': 'confirmed'}
        response = self.client.patch(booking_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'confirmed')
        
        # Check that vehicle status was updated
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, 'rented')
    
    def test_cancel_booking(self):
        """Test cancelling a booking"""
        booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00,
            status='confirmed'
        )
        
        booking_detail_url = reverse('bookings:booking-detail', args=[booking.id])
        data = {'status': 'cancelled'}
        response = self.client.patch(booking_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')
        
        # Check that vehicle status was updated
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, 'available')
    
    def test_delete_booking(self):
        """Test deleting a booking"""
        booking = Booking.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00
        )
        
        booking_detail_url = reverse('bookings:booking-detail', args=[booking.id])
        response = self.client.delete(booking_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Booking.objects.filter(id=booking.id).exists())
    
    def test_booking_requires_authentication(self):
        """Test that booking operations require authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.booking_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_cannot_access_other_user_booking(self):
        """Test that user cannot access other user's booking"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        other_booking = Booking.objects.create(
            customer=other_user,
            vehicle=self.vehicle,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=100.00
        )
        
        other_booking_url = reverse('bookings:booking-detail', args=[other_booking.id])
        response = self.client.get(other_booking_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
