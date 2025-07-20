import random
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from listings.models import Listing, Booking, Review


class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create (default: 20)'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=50,
            help='Number of bookings to create (default: 50)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=100,
            help='Number of reviews to create (default: 100)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        fake = Faker()
        
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Listing.objects.all().delete()
            # Don't delete users as they might be needed elsewhere
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Create users
        users_to_create = options['users']
        existing_users = User.objects.count()
        
        if existing_users < users_to_create:
            self.stdout.write(f'Creating {users_to_create - existing_users} users...')
            users = []
            for i in range(existing_users, users_to_create):
                user = User(
                    username=fake.user_name() + str(i),
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_active=True
                )
                user.set_password('password123')
                users.append(user)
            
            User.objects.bulk_create(users, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users.'))
        
        all_users = list(User.objects.all()[:users_to_create])

        # Create listings
        listings_count = options['listings']
        self.stdout.write(f'Creating {listings_count} listings...')
        
        property_types = [
            'Cozy Studio Apartment',
            'Luxury Villa with Pool',
            'Modern Downtown Loft',
            'Beachfront Condo',
            'Mountain Cabin Retreat',
            'Historic Townhouse',
            'Penthouse Suite',
            'Garden View Apartment',
            'Rustic Farmhouse',
            'City Center Hotel Room'
        ]
        
        locations = [
            'New York, NY',
            'Los Angeles, CA',
            'Miami, FL',
            'Paris, France',
            'London, UK',
            'Tokyo, Japan',
            'Barcelona, Spain',
            'Amsterdam, Netherlands',
            'Sydney, Australia',
            'Rome, Italy',
            'Berlin, Germany',
            'San Francisco, CA',
            'Chicago, IL',
            'Seattle, WA',
            'Boston, MA'
        ]

        listings = []
        for _ in range(listings_count):
            listing = Listing(
                host=random.choice(all_users),
                name=f"{random.choice(property_types)} in {fake.city()}",
                description=fake.text(max_nb_chars=500),
                location=random.choice(locations),
                price_per_night=Decimal(str(random.uniform(50, 500))).quantize(Decimal('0.01')),
                bedrooms=random.randint(1, 5),
                bathrooms=random.randint(1, 4),
                max_guests=random.randint(1, 10),
                is_available=random.choice([True, True, True, False])  # 75% available
            )
            listings.append(listing)
        
        Listing.objects.bulk_create(listings)
        self.stdout.write(self.style.SUCCESS(f'Created {len(listings)} listings.'))
        
        all_listings = list(Listing.objects.all())

        # Create bookings
        bookings_count = options['bookings']
        self.stdout.write(f'Creating {bookings_count} bookings...')
        
        booking_statuses = ['pending', 'confirmed', 'canceled', 'completed']
        bookings = []
        
        for _ in range(bookings_count):
            listing = random.choice(all_listings)
            user = random.choice([u for u in all_users if u != listing.host])  # Guest can't be host
            
            # Generate random dates
            start_date = fake.date_between(start_date='-6m', end_date='+6m')
            duration = random.randint(1, 14)  # 1 to 14 days
            end_date = start_date + timedelta(days=duration)
            
            guests = random.randint(1, min(listing.max_guests, 6))
            total_price = duration * listing.price_per_night
            
            booking = Booking(
                property=listing,
                user=user,
                check_in_date=start_date,
                check_out_date=end_date,
                guests=guests,
                total_price=total_price,
                status=random.choice(booking_statuses)
            )
            bookings.append(booking)
        
        Booking.objects.bulk_create(bookings)
        self.stdout.write(self.style.SUCCESS(f'Created {len(bookings)} bookings.'))

        # Create reviews
        reviews_count = options['reviews']
        self.stdout.write(f'Creating {reviews_count} reviews...')
        
        review_comments = [
            "Amazing place! Highly recommended.",
            "Clean, comfortable, and great location.",
            "Perfect for a weekend getaway.",
            "Host was very responsive and helpful.",
            "Beautiful property with stunning views.",
            "Exactly as described, great value for money.",
            "Loved the amenities and the neighborhood.",
            "Could use some updates but overall good.",
            "Great experience, would book again!",
            "Nice place but a bit noisy at night.",
            "Excellent facilities and very clean.",
            "Perfect location for exploring the city.",
            "Host went above and beyond expectations.",
            "Good value for the price point.",
            "Comfortable bed and great wifi."
        ]
        
        reviews = []
        user_property_pairs = set()
        
        attempts = 0
        while len(reviews) < reviews_count and attempts < reviews_count * 3:
            attempts += 1
            listing = random.choice(all_listings)
            user = random.choice([u for u in all_users if u != listing.host])
            
            # Ensure unique user-property combination
            pair = (user.id, listing.listing_id)
            if pair in user_property_pairs:
                continue
                
            user_property_pairs.add(pair)
            
            review = Review(
                property=listing,
                user=user,
                rating=random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[5, 10, 15, 35, 35]  # Weighted towards higher ratings
                )[0],
                comment=random.choice(review_comments)
            )
            reviews.append(review)
        
        Review.objects.bulk_create(reviews)
        self.stdout.write(self.style.SUCCESS(f'Created {len(reviews)} reviews.'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== SEEDING COMPLETED ==='))
        self.stdout.write(f'Users: {User.objects.count()}')
        self.stdout.write(f'Listings: {Listing.objects.count()}')
        self.stdout.write(f'Bookings: {Booking.objects.count()}')
        self.stdout.write(f'Reviews: {Review.objects.count()}')
        
        # Show some statistics
        self.stdout.write('\n=== STATISTICS ===')
        available_listings = Listing.objects.filter(is_available=True).count()
        self.stdout.write(f'Available listings: {available_listings}')
        
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        self.stdout.write(f'Confirmed bookings: {confirmed_bookings}')
        
        avg_rating = Review.objects.aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating']
        if avg_rating:
            self.stdout.write(f'Average rating: {avg_rating:.2f}')
        
        self.stdout.write(self.style.SUCCESS('\nSeeding completed successfully!'))