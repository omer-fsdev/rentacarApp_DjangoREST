from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Car,Reservation
from .serializers import CarSerializer, ReservationSerializer
from .permissions import IsStaffOrReadOnly
from django.db.models import Q, Exists, OuterRef
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.response import Response

class CarView(ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsStaffOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = super().get_queryset()
        else:
            queryset = super().get_queryset().filter(availability=True)
            
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        
        if start is not None and end is not None:
            # not_available = Reservation.objects.filter(
            #     end_date__gt=start, start_date__lt=end
            # ).values_list('car_id', flat=True)    # flat=True makes it list.
            
            #* with Q library (for complex queries) (from django.db.models import Q):
            # not_available = Reservation.objects.filter(
            #     Q(end_date__gt=start) & Q(start_date__lt=end)
            # ).values_list('car_id', flat=True)
            #* 2. way with Q library:
            # condition1 = Q(start_date__lt=end)
            # condition2 = Q(end_date__gt=start)
            # not_available = Reservation.objects.filter(
            #      condition1 & condition2
            #  ).values_list('car_id', flat=True)
            
            # queryset = queryset.exclude(id__in=not_available)
        
            queryset = queryset.annotate(
                is_available = ~Exists(
                    Reservation.objects.filter(
                        Q(car=OuterRef('pk')) & Q(end_date__gt=start) & Q(start_date__lt=end)
                    )
                )
            )
            
        return queryset
    
class ReservationView(ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:    
            return super().get_queryset()
        return super().get_queryset().filter(customer=self.request.user)
    
class ReservationDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        end = serializer.validated_data.get('end_date')
        start = instance.start_date
        car = instance.car
        today = timezone.now().date()
        if Reservation.objects.filter(car=car, end_date__gte=today):
            for res in Reservation.objects.filter(car=car, end_date__gte=today):
                if start < res.start_date <= end:
                    return Response({'message': 'The car is not available between these dates.'})
        return super().update(request, *args, **kwargs)