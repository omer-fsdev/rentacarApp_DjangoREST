from rest_framework import serializers
from .models import Car, Reservation

class CarSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField()
    
    class Meta:
        model = Car
        fields = (
            'id',
            'plate_number',
            'brand',
            'model',
            'year',
            'gear',
            'rent_per_day',
            'availability',
            'is_available'
        )
        
    def get_fields(self):  # can use instead: create different serializers. override get_serializer_class in views, choose serializers for each user type. 
        fields = super().get_fields()
        request = self.context.get('request')
        
        if request.user and not request.user.is_staff:
            fields.pop('plate_number')
            fields.pop('availability')
            
        return fields
    
class ReservationSerializer(serializers.ModelSerializer):
    
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = ('id', 'customer', 'car', 'start_date', 'end_date', 'total_price')
        
    def get_total_price(self, obj):
        return obj.car.rent_per_day * (obj.end_date - obj.start_date).days
        