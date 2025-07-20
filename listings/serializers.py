from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model to include in other serializers.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model.
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'property', 'user', 'user_id', 
            'rating', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at']

    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for Listing model with nested host information and review statistics.
    """
    host = UserSerializer(read_only=True)
    host_id = serializers.IntegerField(write_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Listing
        fields = [
            'listing_id', 'host', 'host_id', 'name', 'description', 
            'location', 'price_per_night', 'bedrooms', 'bathrooms', 
            'max_guests', 'is_available', 'created_at', 'updated_at',
            'average_rating', 'total_reviews', 'reviews'
        ]
        read_only_fields = ['listing_id', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        """Get the average rating for the listing"""
        return obj.get_average_rating()

    def get_total_reviews(self, obj):
        """Get the total number of reviews for the listing"""
        return obj.get_total_reviews()

    def validate_price_per_night(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price per night must be greater than 0.")
        return value

    def validate_max_guests(self, value):
        """Validate max guests is positive"""
        if value <= 0:
            raise serializers.ValidationError("Max guests must be at least 1.")
        return value


class ListingDetailSerializer(ListingSerializer):
    """
    Detailed serializer for Listing with all reviews included.
    """
    reviews = ReviewSerializer(many=True, read_only=True)


class ListingSummarySerializer(serializers.ModelSerializer):
    """
    Simplified serializer for Listing for list views.
    """
    host_name = serializers.CharField(source='host.username', read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'listing_id', 'name', 'location', 'price_per_night', 
            'bedrooms', 'bathrooms', 'max_guests', 'is_available',
            'host_name', 'average_rating', 'total_reviews'
        ]

    def get_average_rating(self, obj):
        """Get the average rating for the listing"""
        return obj.get_average_rating()

    def get_total_reviews(self, obj):
        """Get the total number of reviews for the listing"""
        return obj.get_total_reviews()


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model with nested property and user information.
    """
    property = ListingSummarySerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'property', 'property_id', 'user', 'user_id',
            'check_in_date', 'check_out_date', 'guests', 'total_price',
            'status', 'created_at', 'updated_at', 'duration_days'
        ]
        read_only_fields = ['booking_id', 'total_price', 'created_at', 'updated_at']

    def get_duration_days(self, obj):
        """Get the duration of the booking in days"""
        return obj.get_duration_days()

    def validate(self, data):
        """Validate booking dates and guest capacity"""
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        guests = data.get('guests')
        property_obj = data.get('property_id')

        # Validate dates
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError({
                    'check_out_date': 'Check-out date must be after check-in date.'
                })

        # Validate guest capacity
        if property_obj and guests:
            try:
                listing = Listing.objects.get(listing_id=property_obj)
                if guests > listing.max_guests:
                    raise serializers.ValidationError({
                        'guests': f'Number of guests exceeds maximum capacity of {listing.max_guests}.'
                    })
            except Listing.DoesNotExist:
                raise serializers.ValidationError({
                    'property_id': 'Invalid property ID.'
                })

        return data

    def create(self, validated_data):
        """Create booking and calculate total price"""
        property_id = validated_data.pop('property_id')
        user_id = validated_data.pop('user_id')
        
        try:
            property_obj = Listing.objects.get(listing_id=property_id)
            user_obj = User.objects.get(id=user_id)
        except (Listing.DoesNotExist, User.DoesNotExist) as e:
            raise serializers.ValidationError(f"Invalid reference: {str(e)}")
        
        # Calculate total price
        duration = (validated_data['check_out_date'] - validated_data['check_in_date']).days
        total_price = duration * property_obj.price_per_night
        
        booking = Booking.objects.create(
            property=property_obj,
            user=user_obj,
            total_price=total_price,
            **validated_data
        )
        return booking


class BookingSummarySerializer(serializers.ModelSerializer):
    """
    Simplified serializer for Booking for list views.
    """
    property_name = serializers.CharField(source='property.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'property_name', 'user_name', 
            'check_in_date', 'check_out_date', 'guests', 
            'total_price', 'status', 'duration_days'
        ]

    def get_duration_days(self, obj):
        """Get the duration of the booking in days"""
        return obj.get_duration_days()