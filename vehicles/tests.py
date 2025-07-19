from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Vehicle

User = get_user_model()


class VehicleModelTest(TestCase):
    """Test cases for Vehicle model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.vehicle_data = {
            'owner': self.user,
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2020,
            'plate_number': 'ABC123',
            'daily_rate': 50.00,
            'fuel_type': 'petrol',
            'transmission': 'automatic',
            'color': 'White',
            'seats': 5
        }
    
    def test_create_vehicle(self):
        """Test creating a new vehicle"""
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        self.assertEqual(vehicle.make, 'Toyota')
        self.assertEqual(vehicle.model, 'Camry')
        self.assertEqual(vehicle.year, 2020)
        self.assertEqual(vehicle.plate_number, 'ABC123')
        self.assertEqual(vehicle.daily_rate, 50.00)
        self.assertEqual(vehicle.status, 'available')
    
    def test_vehicle_str_representation(self):
        """Test vehicle string representation"""
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        expected = "2020 Toyota Camry - ABC123"
        self.assertEqual(str(vehicle), expected)
    
    def test_vehicle_full_name_property(self):
        """Test vehicle full_name property"""
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        expected = "2020 Toyota Camry"
        self.assertEqual(vehicle.full_name, expected)
    
    def test_vehicle_choices(self):
        """Test vehicle choice fields"""
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        self.assertIn(vehicle.fuel_type, dict(Vehicle.FUEL_TYPE_CHOICES))
        self.assertIn(vehicle.transmission, dict(Vehicle.TRANSMISSION_CHOICES))
        self.assertIn(vehicle.status, dict(Vehicle.STATUS_CHOICES))


class VehicleAPITest(APITestCase):
    """Test cases for Vehicle API"""
    
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
        self.client.force_authenticate(user=self.user)
        self.vehicle_list_url = reverse('vehicles:vehicle-list-create')
        self.vehicle_detail_url = reverse('vehicles:vehicle-detail', args=[self.vehicle.id])
    
    def test_list_vehicles(self):
        """Test listing user's vehicles"""
        response = self.client.get(self.vehicle_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['make'], 'Toyota')
    
    def test_create_vehicle(self):
        """Test creating a new vehicle"""
        data = {
            'make': 'Honda',
            'model': 'Civic',
            'year': 2021,
            'plate_number': 'XYZ789',
            'daily_rate': 45.00,
            'fuel_type': 'petrol',
            'transmission': 'manual'
        }
        response = self.client.post(self.vehicle_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['make'], 'Honda')
        self.assertEqual(response.data['owner'], 'testuser')
    
    def test_create_vehicle_with_duplicate_plate(self):
        """Test creating vehicle with duplicate plate number"""
        data = {
            'make': 'Honda',
            'model': 'Civic',
            'year': 2021,
            'plate_number': 'ABC123',  # Same as existing
            'daily_rate': 45.00
        }
        response = self.client.post(self.vehicle_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('plate_number', response.data)
    
    def test_create_vehicle_with_invalid_daily_rate(self):
        """Test creating vehicle with invalid daily rate"""
        data = {
            'make': 'Honda',
            'model': 'Civic',
            'year': 2021,
            'plate_number': 'XYZ789',
            'daily_rate': -10.00  # Negative rate
        }
        response = self.client.post(self.vehicle_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('daily_rate', response.data)
    
    def test_retrieve_vehicle(self):
        """Test retrieving a specific vehicle"""
        response = self.client.get(self.vehicle_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['make'], 'Toyota')
        self.assertEqual(response.data['plate_number'], 'ABC123')
    
    def test_update_vehicle(self):
        """Test updating a vehicle"""
        data = {
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2020,
            'plate_number': 'ABC123',
            'daily_rate': 60.00,  # Updated rate
            'color': 'Blue'  # Added color
        }
        response = self.client.put(self.vehicle_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['daily_rate'], '60.00')
        self.assertEqual(response.data['color'], 'Blue')
    
    def test_delete_vehicle(self):
        """Test deleting a vehicle"""
        response = self.client.delete(self.vehicle_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Vehicle.objects.filter(id=self.vehicle.id).exists())
    
    def test_vehicle_requires_authentication(self):
        """Test that vehicle operations require authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.vehicle_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_cannot_access_other_user_vehicle(self):
        """Test that user cannot access other user's vehicle"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        other_vehicle = Vehicle.objects.create(
            owner=other_user,
            make='Honda',
            model='Civic',
            year=2021,
            plate_number='XYZ789',
            daily_rate=45.00
        )
        other_vehicle_url = reverse('vehicles:vehicle-detail', args=[other_vehicle.id])
        response = self.client.get(other_vehicle_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
