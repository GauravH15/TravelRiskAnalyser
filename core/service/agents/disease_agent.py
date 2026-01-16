"""
Health and Disease Risk Agent
Analyzes disease outbreaks, COVID status, vaccination requirements, and healthcare quality
"""

import json
import logging
from core.service.tools.disease_tools import (
    get_covid_status,
    get_disease_outbreaks,
    get_vaccination_requirements,
    get_healthcare_quality
)
from core.service.llm_recommendations import (
    generate_health_recommendations_llm,
    flatten_recommendations
)

logger = logging.getLogger(__name__)


def disease_agent(trip, traveler) -> dict:
    """
    Agent that analyzes health and disease risks for the destination
    
    Args:
        trip: Trip object with destination
        traveler: Traveler object with health conditions
        
    Returns:
        dict: Structured health and disease risk assessment
    """
    
    try:
        # Get COVID-19 status
        covid_data = get_covid_status(trip.destination_country)
        
        # Get disease outbreak information
        outbreaks = get_disease_outbreaks(trip.destination_country)
        
        # Get vaccination requirements
        vaccines = get_vaccination_requirements(trip.destination_country)
        
        # Get healthcare quality
        healthcare = get_healthcare_quality(trip.destination_country)
        
        # Combine risk scores
        covid_risk = covid_data.get("risk_score", 0) if covid_data.get("status") == "success" else 5
        outbreak_risk = outbreaks.get("risk_score", 0) if outbreaks.get("status") == "success" else 5
        vaccine_risk = 10 if vaccines.get("required_vaccines", []) else 5
        healthcare_risk = healthcare.get("risk_score", 0) if healthcare.get("status") == "success" else 5
        
        # Total health risk score (0-100)
        combined_risk = min((covid_risk + outbreak_risk + vaccine_risk + healthcare_risk) // 2, 100)
        
        # Determine risk level
        risk_level = "Low" if combined_risk < 30 else ("Medium" if combined_risk < 60 else "High")
        
        # Traveler-specific considerations
        special_considerations = []
        if traveler.health_conditions:
            if "diabetes" in traveler.health_conditions.lower():
                special_considerations.append("Ensure adequate insulin/medication supply - healthcare quality varies")
            if "asthma" in traveler.health_conditions.lower():
                special_considerations.append("Check air quality - respiratory conditions may worsen in polluted areas")
            if "immunocompromised" in traveler.health_conditions.lower():
                if covid_risk > 10 or outbreak_risk > 15:
                    special_considerations.append("Higher risk from infections - consider travel insurance")
        
        if not traveler.frequent_traveler and combined_risk > 40:
            special_considerations.append("First-time traveler to high-risk area - consult travel medicine specialist")
        
        return {
            "agent_name": "health_disease",
            "status": "success",
            "risk_score": combined_risk,
            "risk_level": risk_level,
            "covid_19": {
                "risk_level": covid_data.get("risk_level") if covid_data.get("status") == "success" else "Unknown",
                "cases_per_million": covid_data.get("cases_per_million") if covid_data.get("status") == "success" else None,
                "trend": covid_data.get("trend") if covid_data.get("status") == "success" else None,
                "risk_component": covid_risk
            },
            "disease_outbreaks": {
                "endemic_diseases": outbreaks.get("endemic_diseases") if outbreaks.get("status") == "success" else [],
                "vaccination_recommended": outbreaks.get("vaccination_recommended") if outbreaks.get("status") == "success" else False,
                "medical_advice": outbreaks.get("consult_medical_advice") if outbreaks.get("status") == "success" else "Recommended",
                "risk_component": outbreak_risk
            },
            "vaccination_requirements": {
                "required": vaccines.get("required_vaccines") if vaccines.get("status") == "success" else [],
                "recommended": vaccines.get("recommended_vaccines") if vaccines.get("status") == "success" else [],
                "consult_days_before": vaccines.get("consult_before_days") if vaccines.get("status") == "success" else 2,
                "risk_component": vaccine_risk
            },
            "healthcare_infrastructure": {
                "quality_rating": healthcare.get("healthcare_quality") if healthcare.get("status") == "success" else "Unknown",
                "accessibility": healthcare.get("accessibility") if healthcare.get("status") == "success" else "Unknown",
                "cost_level": healthcare.get("estimated_cost_level") if healthcare.get("status") == "success" else "Unknown",
                "recommendation": healthcare.get("recommendation") if healthcare.get("status") == "success" else "Travel insurance recommended",
                "risk_component": healthcare_risk
            },
            "traveler_specific_considerations": special_considerations if special_considerations else ["Standard health precautions"],
            "recommendations": generate_health_recommendations(
                trip, traveler, covid_data, outbreaks, vaccines, healthcare, combined_risk
            )
        }
        
    except Exception as e:
        logger.error(f"Disease agent error: {e}")
        return {
            "agent_name": "health_disease",
            "status": "error",
            "risk_score": 15,
            "message": str(e)
        }


def generate_health_recommendations(trip, traveler, covid_data, outbreaks, vaccines, healthcare, risk_score):
    """
    Generate actionable health recommendations using LLM
    Falls back to simple rules if LLM is unavailable
    """
    
    # Prepare data for LLM
    health_risk_data = {
        "destination": trip.destination_country if hasattr(trip, "destination_country") else "Unknown",
        "health_conditions": traveler.health_conditions if traveler.health_conditions else "None reported",
        "frequent_traveler": traveler.frequent_traveler if hasattr(traveler, "frequent_traveler") else False,
        "covid_data": covid_data if covid_data.get("status") == "success" else {},
        "disease_outbreaks": outbreaks.get("endemic_diseases", []) if outbreaks.get("status") == "success" else [],
        "required_vaccines": vaccines.get("required_vaccines", []) if vaccines.get("status") == "success" else [],
        "recommended_vaccines": vaccines.get("recommended_vaccines", []) if vaccines.get("status") == "success" else [],
        "healthcare_quality": healthcare.get("healthcare_quality", "Unknown") if healthcare.get("status") == "success" else "Unknown",
    }
    
    # Try LLM-based recommendations
    llm_recommendations = generate_health_recommendations_llm(health_risk_data)
    
    if llm_recommendations:
        # Use LLM-generated recommendations
        recommendations = flatten_recommendations(llm_recommendations)
        logger.info(f"Generated {len(recommendations)} health recommendations using LLM")
        return recommendations
    
    # Fallback to rule-based recommendations if LLM fails
    logger.warning("LLM recommendation generation failed, falling back to rule-based recommendations")
    return _generate_fallback_health_recommendations(
        covid_data, outbreaks, vaccines, healthcare, traveler, risk_score
    )


def _generate_fallback_health_recommendations(covid_data, outbreaks, vaccines, healthcare, traveler, risk_score):
    """Fallback rule-based recommendation generator"""
    
    recommendations = []
    
    # Vaccination recommendations
    if vaccines.get("status") == "success":
        required = vaccines.get("required_vaccines", [])
        recommended = vaccines.get("recommended_vaccines", [])
        
        if required and "None" not in str(required[0]):
            recommendations.append(f"GET VACCINATED: {', '.join(required[:2])} - required for entry")
        
        if recommended:
            recommendations.append(f"Recommended vaccines: {', '.join(recommended[:2])}")
    
    # COVID-19 precautions
    if covid_data.get("status") == "success":
        if covid_data.get("risk_level") in ["High", "Very High"]:
            recommendations.append("COVID-19 levels elevated - consider N95 masks in crowded areas")
            recommendations.append("Keep up-to-date with vaccinations")
    
    # Disease outbreak precautions
    if outbreaks.get("status") == "success":
        endemic = outbreaks.get("endemic_diseases", [])
        if endemic and "Standard" not in str(endemic[0]):
            if any("malaria" in d.lower() for d in endemic):
                recommendations.append("Take malaria prophylaxis - start 1-2 days before departure")
            if any("dengue" in d.lower() for d in endemic):
                recommendations.append("Use insect repellent with DEET to prevent dengue/Zika")
    
    # Healthcare recommendations
    if healthcare.get("status") == "success":
        if healthcare.get("healthcare_quality") == "Fair":
            recommendations.append("Download offline copies of your medical records")
            recommendations.append("Identify nearest hospital/clinic to accommodation")
        
        if healthcare.get("estimated_cost_level") == "High":
            recommendations.append("Ensure travel insurance covers high medical costs")
    
    # General recommendations
    if risk_score > 50:
        recommendations.append("Consult a travel medicine specialist before departure")
        recommendations.append("Carry comprehensive travel health insurance")
    
    recommendations.append("Keep medications in original containers with labels")
    recommendations.append("Maintain good hygiene practices - wash hands frequently")
    
    return recommendations

