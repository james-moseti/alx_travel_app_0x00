from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Listing(models.Model):
    """
    Model representing a property listing for travel accommodations.
    """
    listing_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the listing"
    )
    
    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings',
        help_text="The user who owns this listing"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Title/name of the listing"
    )
    
    description = models.TextField(
        help_text="Detailed description of the property"
    )
    
    location = models.CharField(
        max_length=200,
        help_text="Address or location of the property"
    )
    
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price per night in USD"
    )
    
    # Property details
    bedrooms = models.PositiveIntegerField(
        default=1,
        help_text="Number of bedrooms"
    )
    
    bathrooms = models.PositiveIntegerField(
        default=1,
        help_text="Number of bathrooms"
    )
    
    max_guests = models.PositiveIntegerField(
        default=2,
        help_text="Maximum number of guests allowed"
    )
    
    # Availability and status
    is_available = models.BooleanField(
        default=True,
        help_text="Whether the listing is available for booking"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the listing was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the listing was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Property Listing"
        verbose_name_plural = "Property Listings"

    def __str__(self):
        return f"{self.name} - ${self.price_per_night}/night"

    def get_average_rating(self):
        """Calculate the average rating from all reviews"""
        reviews = self.reviews.all()
        if reviews:
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0

    def get_total_reviews(self):
        """Get the total number of reviews"""
        return self.reviews.count()


class Booking(models.Model):
    """
    Model representing a booking for a property listing.
    """
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]
    
    booking_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the booking"
    )
    
    property = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="The property being booked"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="The user making the booking"
    )
    
    check_in_date = models.DateField(
        help_text="Check-in date"
    )
    
    check_out_date = models.DateField(
        help_text="Check-out date"
    )
    
    guests = models.PositiveIntegerField(
        default=1,
        help_text="Number of guests"
    )
    
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total price for the entire stay"
    )
    
    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default='pending',
        help_text="Current status of the booking"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the booking was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the booking was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        # Ensure no double bookings for the same property and dates
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='check_out_after_check_in'
            )
        ]

    def __str__(self):
        return f"Booking {self.booking_id} - {self.property.name}"

    def clean(self):
        """Validate booking dates and guest capacity"""
        from django.core.exceptions import ValidationError
        
        if self.check_out_date <= self.check_in_date:
            raise ValidationError("Check-out date must be after check-in date.")
        
        if self.guests > self.property.max_guests:
            raise ValidationError(f"Number of guests exceeds maximum capacity of {self.property.max_guests}.")

    def get_duration_days(self):
        """Calculate the duration of the stay in days"""
        return (self.check_out_date - self.check_in_date).days

    def save(self, *args, **kwargs):
        """Override save to calculate total price"""
        if self.check_in_date and self.check_out_date and self.property:
            duration = self.get_duration_days()
            self.total_price = duration * self.property.price_per_night
        super().save(*args, **kwargs)


class Review(models.Model):
    """
    Model representing a review for a property listing.
    """
    review_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the review"
    )
    
    property = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The property being reviewed"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The user writing the review"
    )
    
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    
    comment = models.TextField(
        help_text="Written review comment"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the review was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the review was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        # Ensure one review per user per property
        unique_together = ['property', 'user']

    def __str__(self):
        return f"Review by {self.user.username} - {self.rating} stars"