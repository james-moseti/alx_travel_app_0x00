# ALX Travel App

A Django-based travel accommodation booking application with comprehensive listing, booking, and review functionality.

## Features

- **Property Listings**: Create and manage travel accommodation listings
- **Booking System**: Book properties with date validation and pricing calculation
- **Review System**: Rate and review properties with a 5-star system
- **User Management**: User authentication and profile management
- **API Serialization**: RESTful API with comprehensive serializers

## Models

### Listing Model
Represents a travel accommodation property with the following fields:
- `listing_id`: UUID primary key
- `host`: Foreign key to User (property owner)
- `name`: Property title/name
- `description`: Detailed property description
- `location`: Property address/location
- `price_per_night`: Decimal price per night
- `bedrooms`: Number of bedrooms
- `bathrooms`: Number of bathrooms
- `max_guests`: Maximum guest capacity
- `is_available`: Availability status
- `created_at`/`updated_at`: Timestamps

### Booking Model
Represents a property booking with the following fields:
- `booking_id`: UUID primary key
- `property`: Foreign key to Listing
- `user`: Foreign key to User (guest)
- `check_in_date`: Check-in date
- `check_out_date`: Check-out date
- `guests`: Number of guests
- `total_price`: Calculated total price
- `status`: Booking status (pending, confirmed, canceled, completed)
- `created_at`/`updated_at`: Timestamps

### Review Model
Represents a property review with the following fields:
- `review_id`: UUID primary key
- `property`: Foreign key to Listing
- `user`: Foreign key to User (reviewer)
- `rating`: Integer rating (1-5 stars)
- `comment`: Review text
- `created_at`/`updated_at`: Timestamps

## Serializers

The application includes comprehensive API serializers:

- **ListingSerializer**: Full listing details with host info and review statistics
- **ListingSummarySerializer**: Simplified listing view for lists
- **ListingDetailSerializer**: Extended listing view with all reviews
- **BookingSerializer**: Full booking details with validation
- **BookingSummarySerializer**: Simplified booking view
- **ReviewSerializer**: Review serialization with user details
- **UserSerializer**: User information serialization

## Installation

1. **Clone the repository**

2. **Install dependencies**

3. **Run migrations**

4. **Create a superuser** (optional)

## Database Seeding

The application includes a comprehensive management command for seeding the database with sample data.

### Basic Usage
```bash
python manage.py seed
```

### Advanced Usage
```bash
# Create specific amounts of data
python manage.py seed --users 20 --listings 50 --bookings 100 --reviews 200

# Clear existing data before seeding
python manage.py seed --clear

# Create minimal data for testing
python manage.py seed --users 5 --listings 10 --bookings 20 --reviews 30
```

### Seeder Options
- `--users`: Number of users to create (default: 10)
- `--listings`: Number of listings to create (default: 20)
- `--bookings`: Number of bookings to create (default: 50)
- `--reviews`: Number of reviews to create (default: 100)
- `--clear`: Clear existing data before seeding

### Sample Data Generated
The seeder creates realistic sample data including:
- **Users**: With realistic names, usernames, and emails
- **Listings**: Various property types in different locations with realistic pricing
- **Bookings**: Realistic booking patterns with proper date ranges and pricing
- **Reviews**: Weighted ratings (favoring higher ratings) with realistic comments

