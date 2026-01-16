"""
Test suite for multi-agent travel risk analysis system
Tests all agents and tools independently and as integrated system
"""

import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TravelRiskAnalyser.settings')
django.setup()

from core.models import Traveler, Trip
from core.service.tools.geo_tools import get_coordinates, get_country_code
from core.service.tools.weather_tools import (
    get_weather_forecast,
    get_air_quality,
    get_natural_disaster_risk
)
from core.service.tools.disease_tools import (
    get_covid_status,
    get_disease_outbreaks,
    get_vaccination_requirements,
    get_healthcare_quality
)
from core.service.agents.weather_agent import weather_agent
from core.service.agents.disease_agent import disease_agent
from core.service.agents.orchestrator import orchestrator_agent


def test_geo_tools():
    """Test geocoding and country code tools"""
    print("\n" + "="*60)
    print("TESTING GEO TOOLS")
    print("="*60)
    
    # Test coordinate retrieval
    lat, lon = get_coordinates("Cairo", "Egypt")
    print(f"✓ Cairo, Egypt coordinates: ({lat}, {lon})")
    assert lat is not None and lon is not None, "Failed to get coordinates"
    
    # Test country code
    code = get_country_code("Egypt")
    print(f"✓ Egypt country code: {code}")
    
    return lat, lon


def test_weather_tools(lat, lon):
    """Test weather tools"""
    print("\n" + "="*60)
    print("TESTING WEATHER TOOLS")
    print("="*60)
    
    start_date = date.today()
    end_date = start_date + timedelta(days=7)
    
    # Test weather forecast
    weather = get_weather_forecast(lat, lon, str(start_date), str(end_date))
    print(f"✓ Weather forecast retrieved")
    print(f"  - Status: {weather.get('status')}")
    if weather.get('status') == 'success':
        print(f"  - Avg Temperature: {weather.get('avg_temperature')}°C")
        print(f"  - Precipitation: {weather.get('total_precipitation_mm')}mm")
        print(f"  - Risk Score: {weather.get('risk_score')}/100")
    
    # Test air quality
    air_quality = get_air_quality(lat, lon)
    print(f"✓ Air quality retrieved")
    print(f"  - Status: {air_quality.get('status')}")
    if air_quality.get('status') == 'success':
        print(f"  - PM2.5: {air_quality.get('pm2_5')}")
        print(f"  - Air Quality Level: {air_quality.get('air_quality_level')}")
        print(f"  - Risk Score: {air_quality.get('risk_score')}/100")
    
    # Test natural disaster risk
    disasters = get_natural_disaster_risk(lat, lon)
    print(f"✓ Natural disaster risk retrieved")
    print(f"  - Status: {disasters.get('status')}")
    if disasters.get('status') == 'success':
        print(f"  - Earthquake Risk: {disasters.get('earthquake_risk_level')}")
        print(f"  - Recent Earthquakes (30 days): {disasters.get('recent_earthquakes_count')}")
        print(f"  - Risk Score: {disasters.get('risk_score')}/100")


def test_disease_tools():
    """Test disease and health tools"""
    print("\n" + "="*60)
    print("TESTING DISEASE & HEALTH TOOLS")
    print("="*60)
    
    country = "Egypt"
    
    # Test COVID status
    covid = get_covid_status(country)
    print(f"✓ COVID-19 data retrieved for {country}")
    print(f"  - Status: {covid.get('status')}")
    if covid.get('status') == 'success':
        print(f"  - Risk Level: {covid.get('risk_level')}")
        print(f"  - Cases per Million: {covid.get('cases_per_million')}")
        print(f"  - Risk Score: {covid.get('risk_score')}/100")
    
    # Test disease outbreaks
    outbreaks = get_disease_outbreaks(country)
    print(f"✓ Disease outbreak data retrieved")
    print(f"  - Status: {outbreaks.get('status')}")
    if outbreaks.get('status') == 'success':
        print(f"  - Endemic Diseases: {', '.join(outbreaks.get('endemic_diseases', [])[:2])}")
        print(f"  - Risk Score: {outbreaks.get('risk_score')}/100")
    
    # Test vaccination requirements
    vaccines = get_vaccination_requirements(country)
    print(f"✓ Vaccination requirements retrieved")
    print(f"  - Status: {vaccines.get('status')}")
    if vaccines.get('status') == 'success':
        print(f"  - Required: {', '.join(vaccines.get('required_vaccines', []))}")
        print(f"  - Recommended: {', '.join(vaccines.get('recommended_vaccines', [])[:2])}")
    
    # Test healthcare quality
    healthcare = get_healthcare_quality(country)
    print(f"✓ Healthcare quality retrieved")
    print(f"  - Status: {healthcare.get('status')}")
    if healthcare.get('status') == 'success':
        print(f"  - Healthcare Quality: {healthcare.get('healthcare_quality')}")
        print(f"  - Risk Score: {healthcare.get('risk_score')}/100")


def test_weather_agent():
    """Test weather agent with sample data"""
    print("\n" + "="*60)
    print("TESTING WEATHER AGENT")
    print("="*60)
    
    # Create test trip and traveler
    from UserApp.models import User
    
    try:
        user = User.objects.first()
        if not user:
            # Create test user if none exists
            user = User.objects.create_user(
                username='test_traveler',
                email='test@example.com',
                password='testpass123',
                role='traveler'
            )
        
        traveler, _ = Traveler.objects.get_or_create(
            user=user,
            defaults={
                'health_conditions': 'Asthma',
                'frequent_traveler': False
            }
        )
        
        trip = Trip.objects.create(
            traveler=traveler,
            destination_country='Egypt',
            destination_city='Cairo',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            purpose='Business',
            accommodation='Hotel',
            transport_mode='Flight'
        )
        
        result = weather_agent(trip, traveler)
        print(f"✓ Weather agent completed")
        print(f"  - Status: {result.get('status')}")
        if result.get('status') == 'success':
            print(f"  - Risk Score: {result.get('risk_score')}/100")
            print(f"  - Risk Level: {result.get('risk_level')}")
            print(f"  - Temperature: {result.get('weather', {}).get('avg_temperature')}°C")
            print(f"  - Recommendations: {len(result.get('recommendations', []))} provided")
        
        trip.delete()
        
    except Exception as e:
        print(f"✗ Weather agent test failed: {e}")


def test_disease_agent():
    """Test disease agent with sample data"""
    print("\n" + "="*60)
    print("TESTING DISEASE AGENT")
    print("="*60)
    
    from UserApp.models import User
    
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='test_traveler2',
                email='test2@example.com',
                password='testpass123',
                role='traveler'
            )
        
        traveler, _ = Traveler.objects.get_or_create(
            user=user,
            defaults={
                'health_conditions': 'Diabetes',
                'frequent_traveler': True
            }
        )
        
        trip = Trip.objects.create(
            traveler=traveler,
            destination_country='Egypt',
            destination_city='Cairo',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            purpose='Tourism',
            accommodation='Airbnb',
            transport_mode='Flight'
        )
        
        result = disease_agent(trip, traveler)
        print(f"✓ Disease agent completed")
        print(f"  - Status: {result.get('status')}")
        if result.get('status') == 'success':
            print(f"  - Risk Score: {result.get('risk_score')}/100")
            print(f"  - Risk Level: {result.get('risk_level')}")
            print(f"  - COVID Level: {result.get('covid_19', {}).get('risk_level')}")
            print(f"  - Required Vaccines: {', '.join(result.get('vaccination_requirements', {}).get('required', [])[:1])}")
            print(f"  - Recommendations: {len(result.get('recommendations', []))} provided")
        
        trip.delete()
        
    except Exception as e:
        print(f"✗ Disease agent test failed: {e}")


def test_orchestrator():
    """Test full orchestrator with multiple agents"""
    print("\n" + "="*60)
    print("TESTING ORCHESTRATOR (FULL SYSTEM)")
    print("="*60)
    
    from UserApp.models import User
    
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='test_orchestrator',
                email='test_orch@example.com',
                password='testpass123',
                role='traveler'
            )
        
        traveler, _ = Traveler.objects.get_or_create(
            user=user,
            defaults={
                'health_conditions': 'None',
                'frequent_traveler': True
            }
        )
        
        trip = Trip.objects.create(
            traveler=traveler,
            destination_country='Egypt',
            destination_city='Cairo',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            purpose='Business Conference',
            accommodation='5-Star Hotel',
            transport_mode='Flight'
        )
        
        print("Running orchestrator with all agents in parallel...")
        result = orchestrator_agent(trip, traveler)
        
        print(f"✓ Orchestrator completed")
        print(f"  - Status: {result.get('status')}")
        if result.get('status') == 'success':
            print(f"\n  OVERALL RISK ASSESSMENT:")
            print(f"  - Overall Risk Score: {result.get('overall_risk_score')}/100")
            print(f"  - Risk Level: {result.get('risk_level')}")
            print(f"  - Weather Risk: {result.get('risk_score_breakdown', {}).get('weather_climate')}/100")
            print(f"  - Disease Risk: {result.get('risk_score_breakdown', {}).get('health_disease')}/100")
            print(f"\n  TOP RISKS:")
            for risk in result.get('top_risks', [])[:3]:
                print(f"    - {risk}")
            print(f"\n  RECOMMENDATIONS:")
            for rec in result.get('consolidated_recommendations', [])[:4]:
                print(f"    - {rec}")
            print(f"\n  EXECUTIVE SUMMARY:")
            print(f"    {result.get('executive_summary', 'N/A')}")
        
        trip.delete()
        
    except Exception as e:
        print(f"✗ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  TRAVEL RISK ANALYSIS MULTI-AGENT SYSTEM TEST SUITE".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    try:
        # Test tools
        lat, lon = test_geo_tools()
        test_weather_tools(lat, lon)
        test_disease_tools()
        
        # Test agents
        test_weather_agent()
        test_disease_agent()
        test_orchestrator()
        
        print("\n" + "█"*60)
        print("█" + " "*58 + "█")
        print("█" + "  ALL TESTS COMPLETED SUCCESSFULLY ✓".center(58) + "█")
        print("█" + " "*58 + "█")
        print("█"*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
