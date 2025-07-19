# Lahore Car Rental - Backend API

A Django REST API backend for Lahore Car Rental. This API provides comprehensive functionality for user authentication, vehicle management, and booking operations for a car rental service.

## About 1Now

**What 1Now does:** 1Now builds comprehensive software solutions for independent car rental companies, providing them with the tools they need to manage their entire rental operation digitally. Their platform includes online booking systems, rental agreement management, calendar scheduling, and payment processing - essentially everything a small to medium car rental business needs to compete with larger players.

**Who it serves:** 1Now serves independent car rental operators like LahoreCarRental.com - small to medium-sized businesses that need professional-grade software to manage their fleet, handle customer bookings, process payments, and maintain rental agreements without the overhead of building custom solutions.

**How this backend connects to LahoreCarRental.com frontend:** This Django REST API serves as the complete backend infrastructure for LahoreCarRental.com's frontend. The frontend would use these REST endpoints to handle user registration/login, display available vehicles, manage booking calendars, process rental agreements, and handle payment flows. The JWT authentication ensures secure user sessions, while the modular API design allows the frontend to build a seamless booking experience with real-time vehicle availability, booking management, and user profile features.

## Features

### ✅ Core Requirements
- **User Authentication**: JWT-based authentication with registration and login
- **Vehicle Management**: Full CRUD operations for vehicles with user scoping
- **Booking Management**: Create, view, and manage bookings with overlap prevention
- **RESTful API**: All endpoints follow REST principles with proper HTTP methods
- **Input Validation**: Comprehensive validation with clear error messages
- **Error Handling**: Graceful error handling with useful response messages
- **Security**: JWT authentication with proper user permissions and scoping

### ✅ Bonus Features
- **Booking Overlap Prevention**: Prevents double-booking of vehicles
- **Mock Stripe Integration**: Deposit system with payment tracking
- **Custom Validators**: Comprehensive input validation for all models
- **Query Filters**: Advanced filtering for bookings (by date, status, vehicle)
- **Admin Interface**: Full Django admin integration for all models
- **Swagger Documentation**: Interactive API documentation with examples

## Technology Stack

- **Django 4.2.7**: Web framework
- **Django REST Framework**: API framework
- **JWT Authentication**: Secure token-based authentication
- **PostgreSQL**: Database
- **Django Filters**: Advanced query filtering
- **CORS Headers**: Cross-origin resource sharing support
- **drf-spectacular**: Swagger/OpenAPI documentation



### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lahore_car_rental
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**
   ```bash
   # Create database
   createdb lahore_car_rental
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE lahore_car_rental;
   \q
   ```

5. **Configure environment variables (optional)**
   ```bash
   # Copy the example environment file
   cp .env .env
   
   # Edit .env with your database credentials
   nano .env
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

## API Documentation

Once the server is running, you can access the API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/

## Testing

Run the test suite:
```bash
python manage.py test
```

The project includes comprehensive tests for:
- User registration and authentication
- Vehicle CRUD operations
- Booking creation and management
- Input validation and error handling
- User permission scoping


