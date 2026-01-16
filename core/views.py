from django.shortcuts import render,HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from UserApp.permissions import IsAdminOrHR, IsTraveler
from .models import Traveler, Trip, RiskAnalysisReport
from .serializers import TravelerSerializer , TripSerializer, RiskAnalysisReportSerializer
from core.service.agents.orchestrator import orchestrator_agent


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
        """
        Multi-agent risk analysis endpoint
        Runs weather, disease, and other agents in parallel
        """
        trip = self.get_object()
        traveler = trip.traveler

        # Run multi-agent orchestrator
        analysis_result = orchestrator_agent(trip, traveler)
        
        if analysis_result.get("status") == "success":
            # Store the analysis result in database
            report, created = RiskAnalysisReport.objects.update_or_create(
                trip=trip,
                defaults={
                    "overall_risk_score": analysis_result.get("overall_risk_score", 0),
                    "weather_risk_score": analysis_result.get("risk_score_breakdown", {}).get("weather_climate", 0),
                    "disease_risk_score": analysis_result.get("risk_score_breakdown", {}).get("health_disease", 0),
                    "full_report": analysis_result,
                    "top_risks": analysis_result.get("top_risks", []),
                    "recommendations": analysis_result.get("consolidated_recommendations", []),
                    "executive_summary": analysis_result.get("executive_summary", ""),
                    "weather_report": analysis_result.get("agent_reports", {}).get("weather_climate", {}),
                    "disease_report": analysis_result.get("agent_reports", {}).get("health_disease", {}),
                }
            )
            
            return Response({
                "status": "success",
                "message": "Risk analysis completed",
                "analysis": analysis_result,
                "report_saved": True
            })
        else:
            return Response({
                "status": "error",
                "message": analysis_result.get("message", "Analysis failed"),
                "overall_risk_score": 50,
                "risk_level": "Unknown"
            }, status=400)    


