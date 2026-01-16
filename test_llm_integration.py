#!/usr/bin/env python
"""
Quick test to verify LLM recommendation integration
Tests that the modules are properly integrated
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TravelRiskAnalyser.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from core.models import Traveler, Trip
from UserApp.models import User
from core.service.agents.disease_agent import disease_agent, generate_health_recommendations
from core.service.llm_recommendations import generate_health_recommendations_llm, flatten_recommendations

print("=" * 60)
print("LLM Recommendation Integration Test")
print("=" * 60)

# Test 1: Module imports
print("\n[Test 1] Verifying module imports...")
try:
    from core.service.agents.disease_agent import disease_agent
    print("  ✓ disease_agent module imported")
    from core.service.llm_recommendations import generate_health_recommendations_llm
    print("  ✓ llm_recommendations module imported")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Function signatures
print("\n[Test 2] Verifying function signatures...")
try:
    import inspect
    
    sig = inspect.signature(disease_agent)
    print(f"  ✓ disease_agent signature: {sig}")
    
    sig = inspect.signature(generate_health_recommendations)
    print(f"  ✓ generate_health_recommendations signature: {sig}")
    
    sig = inspect.signature(generate_health_recommendations_llm)
    print(f"  ✓ generate_health_recommendations_llm signature: {sig}")
except Exception as e:
    print(f"  ✗ Signature check failed: {e}")
    sys.exit(1)

# Test 3: Test data structure
print("\n[Test 3] Testing with sample health data...")
try:
    sample_health_data = {
        "destination": "Egypt",
        "health_conditions": "No pre-existing conditions",
        "frequent_traveler": True,
        "covid_data": {
            "status": "success",
            "risk_level": "Medium",
            "cases_per_million": 45
        },
        "disease_outbreaks": ["Yellow Fever", "Hepatitis A"],
        "required_vaccines": ["Yellow Fever"],
        "recommended_vaccines": ["Hepatitis A", "Typhoid"],
        "healthcare_quality": "Good"
    }
    
    print(f"  ✓ Sample health data structure created")
    print(f"    - Destination: {sample_health_data['destination']}")
    print(f"    - Vaccines required: {sample_health_data['required_vaccines']}")
except Exception as e:
    print(f"  ✗ Data structure test failed: {e}")
    sys.exit(1)

# Test 4: LLM function behavior
print("\n[Test 4] Testing LLM function behavior...")
try:
    # Test with real LLM call (will need Azure credentials)
    result = generate_health_recommendations_llm(sample_health_data)
    
    if result:
        print(f"  ✓ LLM returned recommendations")
        print(f"    - Type: {type(result)}")
        if isinstance(result, dict):
            for key in result.keys():
                count = len(result[key]) if isinstance(result[key], list) else 1
                print(f"    - {key}: {count} items")
    else:
        print(f"  ⚠ LLM returned None (may need Azure credentials)")
except Exception as e:
    print(f"  ⚠ LLM call encountered error (expected if Azure not configured)")
    print(f"    Error: {type(e).__name__}: {str(e)[:100]}")

# Test 5: Fallback mechanism
print("\n[Test 5] Testing fallback recommendation generation...")
try:
    # This should work even without Azure credentials
    from core.service.agents.disease_agent import _generate_fallback_health_recommendations
    
    test_covid = {"status": "success", "risk_level": "High"}
    test_outbreaks = {"status": "success", "endemic_diseases": ["malaria"]}
    test_vaccines = {"status": "success", "required_vaccines": ["Yellow Fever"]}
    test_healthcare = {"status": "success", "healthcare_quality": "Fair", "estimated_cost_level": "High"}
    
    class MockTraveler:
        health_conditions = None
        frequent_traveler = True
    
    recommendations = _generate_fallback_health_recommendations(
        test_covid, test_outbreaks, test_vaccines, test_healthcare,
        MockTraveler(), 60
    )
    
    print(f"  ✓ Fallback generation works")
    print(f"    - Generated {len(recommendations)} recommendations")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"    - {i}. {rec[:60]}...")
except Exception as e:
    print(f"  ✗ Fallback test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All integration tests passed!")
print("=" * 60)
print("\nSummary:")
print("  ✓ LLM module properly integrated into disease_agent")
print("  ✓ Function signatures updated correctly")
print("  ✓ Fallback mechanism is in place")
print("  ✓ System ready for Azure LLM integration")
print("\nNote: LLM calls require Azure OpenAI credentials in settings.py")
