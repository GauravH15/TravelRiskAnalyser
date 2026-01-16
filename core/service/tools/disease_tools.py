"""
Disease and health tools for travel risk analysis
Uses disease.sh API (FREE, no key needed) and other free health data sources
"""

import requests
import logging

logger = logging.getLogger(__name__)


def get_covid_status(country: str) -> dict:
    """
    Get COVID-19 status for a country using disease.sh API (FREE)
    
    Args:
        country: Country name
        
    Returns:
        dict: COVID-19 data and risk assessment
    """
    try:
        # Try to get country specific data
        url = f"https://disease.sh/v3/covid-19/countries/{country}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Calculate risk score based on cases and deaths
            cases = data.get("cases", 0)
            deaths = data.get("deaths", 0)
            cases_per_million = data.get("casesPerOneMillion", 0)
            
            risk_score = 0
            status = "Low"
            
            if cases_per_million > 10000:
                risk_score = 25
                status = "Very High"
            elif cases_per_million > 5000:
                risk_score = 20
                status = "High"
            elif cases_per_million > 1000:
                risk_score = 10
                status = "Moderate"
            else:
                risk_score = 5
                status = "Low"
            
            return {
                "status": "success",
                "risk_level": status,
                "total_cases": cases,
                "total_deaths": deaths,
                "cases_per_million": round(cases_per_million, 0),
                "updated": data.get("updated"),
                "risk_score": risk_score,
                "trend": "Check latest updates" if cases_per_million > 1000 else "Minimal concern"
            }
        
        return {"status": "error", "message": "Country not found", "risk_score": 0}
        
    except Exception as e:
        logger.error(f"Error fetching COVID status: {e}")
        return {"status": "error", "message": str(e), "risk_score": 0}


def get_disease_outbreaks(country: str) -> dict:
    """
    Get disease outbreak information for a country
    Uses ProMED and WHO data (via disease.sh aggregation)
    
    Args:
        country: Country name
        
    Returns:
        dict: Disease outbreak assessment
    """
    try:
        # Using disease.sh as aggregator for multiple diseases
        # Note: disease.sh primarily focuses on COVID, but we can check for other data
        
        risk_score = 0
        diseases = []
        
        # Common disease risks by region (simplified mapping)
        # In production, integrate with WHO or ProMED RSS
        regional_diseases = {
            "Africa": ["Malaria", "Dengue", "Yellow Fever", "Ebola (specific regions)"],
            "Asia": ["Dengue", "Malaria", "Zika", "Japanese Encephalitis", "Typhoid"],
            "South America": ["Dengue", "Zika", "Malaria", "Yellow Fever"],
            "Middle East": ["MERS-CoV", "Typhoid", "Hepatitis A"],
            "Europe": ["Tick-borne encephalitis (Eastern)"],
            "North America": ["Lyme Disease", "West Nile Virus"]
        }
        
        # Check country against regions
        africa_countries = ["Egypt", "Kenya", "Nigeria", "South Africa", "Ghana", "Ethiopia", "Uganda"]
        asia_countries = ["Thailand", "Vietnam", "India", "Philippines", "Indonesia", "Myanmar", "Cambodia"]
        americas_countries = ["Brazil", "Colombia", "Peru", "Mexico"]
        
        if any(c in country for c in africa_countries):
            diseases = regional_diseases["Africa"]
            risk_score = 25
        elif any(c in country for c in asia_countries):
            diseases = regional_diseases["Asia"]
            risk_score = 20
        elif any(c in country for c in americas_countries):
            diseases = regional_diseases["South America"]
            risk_score = 15
        else:
            risk_score = 5
            diseases = ["Standard travel vaccinations recommended"]
        
        return {
            "status": "success",
            "risk_score": risk_score,
            "endemic_diseases": diseases,
            "vaccination_recommended": True if risk_score > 10 else False,
            "consult_medical_advice": "Highly recommended" if risk_score > 20 else "Recommended"
        }
        
    except Exception as e:
        logger.error(f"Error fetching disease outbreaks: {e}")
        return {"status": "error", "message": str(e), "risk_score": 0}


def get_vaccination_requirements(country: str) -> dict:
    """
    Get vaccination requirements for a country using REST Countries API
    
    Args:
        country: Country name
        
    Returns:
        dict: Vaccination requirements
    """
    try:
        # Try REST Countries API first
        url = f"https://restcountries.com/v3.1/name/{country}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()[0]
            
            # Common vaccines by region (simplified)
            # In production, use WHO or official government sources
            country_name = data.get("name", {}).get("common", "")
            
            required_vaccines = []
            recommended_vaccines = []
            
            # Yellow Fever required/recommended list (simplified)
            yellow_fever_countries = ["Brazil", "Peru", "Bolivia", "Venezuela", "Colombia", "Ecuador",
                                     "Guyana", "Suriname", "French Guiana", "Egypt", "Kenya", "Uganda"]
            
            # Malaria risk countries
            malaria_countries = ["Nigeria", "Kenya", "Tanzania", "Uganda", "Ghana", "Mozambique",
                               "Zambia", "Zimbabwe", "Malawi", "Thailand", "Myanmar", "Cambodia"]
            
            if any(c in country_name for c in yellow_fever_countries):
                required_vaccines.append("Yellow Fever")
            
            if any(c in country_name for c in malaria_countries):
                recommended_vaccines.append("Malaria Prophylaxis")
            
            # Standard recommendations for all
            recommended_vaccines.extend(["Hepatitis A", "Typhoid", "Routine Vaccinations"])
            
            return {
                "status": "success",
                "country": country_name,
                "required_vaccines": list(set(required_vaccines)) if required_vaccines else ["None specific"],
                "recommended_vaccines": list(set(recommended_vaccines)),
                "consult_before_days": 4 if required_vaccines else 2
            }
        
        return {
            "status": "success",
            "country": country,
            "required_vaccines": ["None specific"],
            "recommended_vaccines": ["Hepatitis A", "Typhoid", "Routine Vaccinations"],
            "consult_before_days": 2
        }
        
    except Exception as e:
        logger.error(f"Error fetching vaccination requirements: {e}")
        return {
            "status": "error",
            "message": str(e),
            "required_vaccines": [],
            "recommended_vaccines": ["Consult travel health professional"]
        }


def get_healthcare_quality(country: str) -> dict:
    """
    Get healthcare infrastructure quality assessment for a country
    
    Args:
        country: Country name
        
    Returns:
        dict: Healthcare quality metrics
    """
    try:
        # Simplified healthcare quality assessment
        # In production, use WHO HAQ Index or similar metrics
        
        high_quality_countries = ["UK", "USA", "Canada", "Australia", "Germany", "France", 
                                 "Japan", "Singapore", "South Korea", "UAE"]
        medium_quality_countries = ["Thailand", "Mexico", "Turkey", "Brazil", "Costa Rica",
                                   "India", "Philippines"]
        
        quality_rating = "High"
        accessibility = "Good"
        cost_level = "Moderate"
        risk_score = 5
        
        if any(c in country for c in high_quality_countries):
            quality_rating = "Excellent"
            accessibility = "Excellent"
            cost_level = "High"
            risk_score = 0
        elif any(c in country for c in medium_quality_countries):
            quality_rating = "Good"
            accessibility = "Good"
            cost_level = "Moderate"
            risk_score = 5
        else:
            quality_rating = "Fair"
            accessibility = "Limited in remote areas"
            cost_level = "Low to Moderate"
            risk_score = 15
        
        return {
            "status": "success",
            "healthcare_quality": quality_rating,
            "accessibility": accessibility,
            "estimated_cost_level": cost_level,
            "risk_score": risk_score,
            "recommendation": "Travel insurance highly recommended" if risk_score > 10 else "Travel insurance recommended"
        }
        
    except Exception as e:
        logger.error(f"Error assessing healthcare quality: {e}")
        return {"status": "error", "message": str(e), "risk_score": 10}
