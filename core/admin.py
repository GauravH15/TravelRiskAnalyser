from django.contrib import admin
from .models import Traveler, Trip, RiskAnalysisReport
# Register your models here.

admin.site.register(Traveler)
admin.site.register(Trip)
admin.site.register(RiskAnalysisReport)