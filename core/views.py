from django.shortcuts import render,HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from UserApp.permissions import IsAdminOrHR, IsTraveler
from .models import Traveler, Trip
from .serializers import TravelerSerializer , TripSerializer
from core.service.azure_openai import analyze_trip_risk


# Create your views here.
def index(request):
    return HttpResponse("User App is working!")


class TravelerViewSet(ModelViewSet):
    serializer_class = TravelerSerializer
    queryset = Traveler.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class TripViewSet(ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role in ["admin", "hr_manager"]:
            return Trip.objects.select_related("traveler", "traveler__user")

        if user.role == "traveler":
            return Trip.objects.filter(traveler__user=user)

        return Trip.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == "traveler":
            traveler = Traveler.objects.get(user=user)
        else:
            traveler_id = self.request.data.get("traveler")
            if not traveler_id:
                raise PermissionDenied("Traveler is required")
            traveler = Traveler.objects.get(id=traveler_id)

        serializer.save(traveler=traveler)

    @action(detail=True, methods=["post"], url_path="analyze-risk")
    def analyze_risk(self, request, pk=None):
        trip = self.get_object()
        traveler = trip.traveler

        result = analyze_trip_risk(trip, traveler)

        return Response(result)    


