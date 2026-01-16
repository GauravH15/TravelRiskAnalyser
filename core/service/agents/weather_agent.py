"""
Weather and Climate Risk Agent
Analyzes weather conditions, air quality, and natural disaster risks for the trip destination
"""

import json
import logging
from core.service.tools.weather_tools import (
    get_weather_forecast,
    get_air_quality,
    get_natural_disaster_risk
)
from core.service.tools.geo_tools import get_coordinates
from core.service.llm_recommendations import (
    generate_health_recommendations_llm,
    flatten_recommendations
)

logger = logging.getLogger(__name__)


def weather_agent(trip, traveler) -> dict:
    """
    Agent that analyzes weather, climate, and natural disaster risks
    
    Args:
        trip: Trip object with destination and dates
        traveler: Traveler object with health conditions
        
    Returns:
        dict: Structured risk assessment from weather perspective
    """
    
    try:
        # Get coordinates for the destination
        lat, lon = get_coordinates(trip.destination_city, trip.destination_country)
        
        if lat is None or lon is None:
            return {
                "agent_name": "weather_climate",
                "status": "error",
                "risk_score": 10,
                "message": "Could not determine destination coordinates"
            }
        
        # Fetch weather data for trip dates
        weather_data = get_weather_forecast(
            lat, lon,
            str(trip.start_date),
            str(trip.end_date)
        )
        
        # Get air quality
        air_quality = get_air_quality(lat, lon)
        
        # Get natural disaster risk
        disasters = get_natural_disaster_risk(lat, lon)
        
        # Combine risk scores
        weather_risk = weather_data.get("risk_score", 0) if weather_data.get("status") == "success" else 10
        air_risk = air_quality.get("risk_score", 0) if air_quality.get("status") == "success" else 5
        disaster_risk = disasters.get("risk_score", 0) if disasters.get("status") == "success" else 0
        
        # Total weather risk score (0-100)
        combined_risk = min((weather_risk + air_risk + disaster_risk) // 2, 100)
        
        # Determine risk level
        risk_level = "Low" if combined_risk < 30 else ("Medium" if combined_risk < 60 else "High")
        
        # Health impact assessment for traveler
        health_impact = []
        if traveler.health_conditions:
            if "asthma" in traveler.health_conditions.lower():
                if air_quality.get("risk_score", 0) > 10:
                    health_impact.append("Air pollution may worsen asthma symptoms")
            if "respiratory" in traveler.health_conditions.lower():
                if weather_data.get("weather_description"):
                    if "heat" in weather_data.get("weather_description", "").lower():
                        health_impact.append("High heat may affect respiratory condition")
        
        return {
            "agent_name": "weather_climate",
            "status": "success",
            "risk_score": combined_risk,
            "risk_level": risk_level,
            "weather": {
                "avg_temperature": weather_data.get("avg_temperature") if weather_data.get("status") == "success" else None,
                "temperature_range": f"{weather_data.get('min_temperature')}-{weather_data.get('max_temperature')}" if weather_data.get("status") == "success" else None,
                "precipitation_mm": weather_data.get("total_precipitation_mm") if weather_data.get("status") == "success" else None,
                "weather_description": weather_data.get("weather_description") if weather_data.get("status") == "success" else "Unknown",
                "risk_component": weather_risk
            },
            "air_quality": {
                "pm2_5": air_quality.get("pm2_5") if air_quality.get("status") == "success" else None,
                "quality_level": air_quality.get("air_quality_level") if air_quality.get("status") == "success" else "Unknown",
                "health_impact": air_quality.get("health_impact") if air_quality.get("status") == "success" else None,
                "risk_component": air_risk
            },
            "natural_disasters": {
                "earthquake_risk": disasters.get("earthquake_risk_level") if disasters.get("status") == "success" else "Unknown",
                "recent_activity": disasters.get("recent_earthquakes_count") if disasters.get("status") == "success" else 0,
                "risk_component": disaster_risk
            },
            "traveler_health_considerations": health_impact if health_impact else ["No specific health concerns"],
            "recommendations": generate_weather_recommendations(
                trip, weather_data, air_quality, disasters, combined_risk
            )
        }
        
    except Exception as e:
        logger.error(f"Weather agent error: {e}")
        return {
            "agent_name": "weather_climate",
            "status": "error",
            "risk_score": 10,
            "message": str(e)
        }


def generate_weather_recommendations(trip, weather_data, air_quality, disasters, risk_score):
    """
    Generate actionable weather recommendations using LLM
    Falls back to simple rules if LLM is unavailable
    """
    
    # Prepare data for LLM
    weather_risk_data = {
        "destination": trip.destination_country if hasattr(trip, "destination_country") else "Unknown",
        "avg_temperature": weather_data.get("avg_temperature") if weather_data.get("status") == "success" else None,
        "temperature_range": f"{weather_data.get('min_temperature')}-{weather_data.get('max_temperature')}" if weather_data.get("status") == "success" else None,
        "precipitation_mm": weather_data.get("total_precipitation_mm") if weather_data.get("status") == "success" else 0,
        "weather_description": weather_data.get("weather_description") if weather_data.get("status") == "success" else "Unknown",
        "wind_speed_kmh": weather_data.get("max_wind_speed_kmh") if weather_data.get("status") == "success" else 0,
        "pm2_5": air_quality.get("pm2_5") if air_quality.get("status") == "success" else None,
        "air_quality_level": air_quality.get("air_quality_level") if air_quality.get("status") == "success" else "Unknown",
        "earthquake_risk": disasters.get("earthquake_risk_level") if disasters.get("status") == "success" else "Unknown",
        "recent_earthquakes": disasters.get("recent_earthquakes_count") if disasters.get("status") == "success" else 0,
    }
    
    # Try LLM-based recommendations
    llm_recommendations = generate_health_recommendations_llm(weather_risk_data)
    
    if llm_recommendations:
        # Use LLM-generated recommendations
        recommendations = flatten_recommendations(llm_recommendations)
        logger.info(f"Generated {len(recommendations)} weather recommendations using LLM")
        return recommendations
    
    # Fallback to rule-based recommendations if LLM fails
    logger.warning("LLM weather recommendation generation failed, falling back to rule-based recommendations")
    return _generate_fallback_weather_recommendations(weather_data, air_quality, risk_score)


def _generate_fallback_weather_recommendations(weather_data, air_quality, risk_score):
    """Fallback rule-based weather recommendation generator"""
    
    recommendations = []
    
    if weather_data.get("status") == "success":
        if weather_data.get("avg_temperature", 0) > 35:
            recommendations.append("Pack light, breathable clothing and high SPF sunscreen")
            recommendations.append("Stay hydrated - drink at least 3 liters of water daily")
        
        if weather_data.get("total_precipitation_mm", 0) > 100:
            recommendations.append("Pack waterproof gear and plan for rainy days")
            recommendations.append("Be cautious of flooding in low-lying areas")
        
        if weather_data.get("max_wind_speed_kmh", 0) > 50:
            recommendations.append("Monitor weather alerts - strong winds possible")
    
    if air_quality.get("status") == "success":
        if air_quality.get("risk_score", 0) > 15:
            recommendations.append("Consider bringing N95 masks for air pollution protection")
            recommendations.append("Limit outdoor activities during peak pollution hours")
    
    if risk_score > 50:
        recommendations.append("Monitor weather and local alerts daily during trip")
        recommendations.append("Share itinerary with emergency contacts")
    
    if not recommendations:
        recommendations.append("Standard weather precautions - monitor local forecast")
    
    return recommendations
