"""
Orchestrator Agent
Coordinates multiple risk analysis agents and aggregates their results
"""

import asyncio
import json
import logging
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor

from core.service.agents.weather_agent import weather_agent
from core.service.agents.disease_agent import disease_agent

logger = logging.getLogger(__name__)


def orchestrator_agent(trip, traveler) -> dict:
    """
    Main orchestrator that coordinates all risk analysis agents
    Runs agents in parallel and aggregates results
    
    Args:
        trip: Trip object
        traveler: Traveler object
        
    Returns:
        dict: Comprehensive risk analysis with all agent reports and aggregated score
    """
    
    try:
        # Run agents in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all agent tasks
            weather_task = executor.submit(weather_agent, trip, traveler)
            disease_task = executor.submit(disease_agent, trip, traveler)
            
            # Get results
            weather_result = weather_task.result()
            disease_result = disease_task.result()
        
        # Aggregate results
        aggregated_report = aggregate_agent_results(
            weather_result,
            disease_result,
            trip,
            traveler
        )
        
        return aggregated_report
        
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        return {
            "status": "error",
            "message": f"Risk analysis failed: {str(e)}",
            "overall_risk_score": 50,
            "risk_level": "Unknown"
        }


def aggregate_agent_results(weather_report: dict, disease_report: dict, trip, traveler) -> dict:
    """
    Aggregate individual agent results into comprehensive report
    
    Args:
        weather_report: Output from weather agent
        disease_report: Output from disease agent
        trip: Trip object
        traveler: Traveler object
        
    Returns:
        dict: Aggregated risk report
    """
    
    # Extract risk scores
    weather_score = weather_report.get("risk_score", 25) if weather_report.get("status") == "success" else 25
    disease_score = disease_report.get("risk_score", 25) if disease_report.get("status") == "success" else 25
    
    # Calculate overall risk score (average of agents)
    overall_risk_score = int((weather_score + disease_score) / 2)
    
    # Determine overall risk level
    if overall_risk_score < 30:
        overall_risk_level = "Low"
    elif overall_risk_score < 60:
        overall_risk_level = "Medium"
    else:
        overall_risk_level = "High"
    
    # Identify top risks
    top_risks = []
    
    # From weather
    if weather_report.get("status") == "success":
        if weather_report.get("risk_level") in ["High", "Medium"]:
            weather_desc = weather_report.get("weather", {}).get("weather_description", "Unknown weather conditions")
            top_risks.append(f"Weather: {weather_desc}")
        if weather_report.get("air_quality", {}).get("risk_component", 0) > 10:
            top_risks.append(f"Air Quality: {weather_report.get('air_quality', {}).get('quality_level', 'Poor')}")
    
    # From disease
    if disease_report.get("status") == "success":
        if disease_report.get("risk_level") in ["High", "Medium"]:
            endemic = disease_report.get("disease_outbreaks", {}).get("endemic_diseases", [])
            if endemic and "Standard" not in str(endemic[0]):
                top_risks.append(f"Disease Risk: {', '.join(endemic[:2])}")
        
        required_vaccines = disease_report.get("vaccination_requirements", {}).get("required", [])
        if required_vaccines and "None" not in str(required_vaccines[0]):
            top_risks.append(f"Vaccination Required: {required_vaccines[0]}")
    
    # Consolidate recommendations
    consolidated_recommendations = []
    
    if weather_report.get("status") == "success":
        consolidated_recommendations.extend(weather_report.get("recommendations", [])[:2])
    
    if disease_report.get("status") == "success":
        consolidated_recommendations.extend(disease_report.get("recommendations", [])[:2])
    
    consolidated_recommendations.append("Maintain emergency contact information")
    consolidated_recommendations.append("Share trip itinerary with family/colleagues")
    
    return {
        "status": "success",
        "trip_id": trip.id,
        "destination": f"{trip.destination_city}, {trip.destination_country}",
        "travel_dates": {
            "start": str(trip.start_date),
            "end": str(trip.end_date),
            "duration_days": (trip.end_date - trip.start_date).days
        },
        "traveler": {
            "id": traveler.id,
            "health_conditions": traveler.health_conditions or "None reported",
            "frequent_traveler": traveler.frequent_traveler
        },
        
        # Overall Risk Assessment
        "overall_risk_score": overall_risk_score,
        "risk_level": overall_risk_level,
        "risk_score_breakdown": {
            "weather_climate": weather_score,
            "health_disease": disease_score
        },
        
        # Top Risks
        "top_risks": top_risks if top_risks else ["No significant risks identified"],
        
        # Detailed Reports from Agents
        "agent_reports": {
            "weather_climate": weather_report,
            "health_disease": disease_report
        },
        
        # Consolidated Recommendations
        "consolidated_recommendations": consolidated_recommendations,
        
        # Executive Summary
        "executive_summary": generate_executive_summary(
            overall_risk_score,
            overall_risk_level,
            top_risks,
            trip,
            traveler
        )
    }


def generate_executive_summary(risk_score: int, risk_level: str, top_risks: List[str], trip, traveler) -> str:
    """
    Generate human-readable executive summary
    
    Args:
        risk_score: Overall risk score (0-100)
        risk_level: Risk level (Low/Medium/High)
        top_risks: List of identified risks
        trip: Trip object
        traveler: Traveler object
        
    Returns:
        str: Executive summary text
    """
    
    duration = (trip.end_date - trip.start_date).days
    
    summary_parts = [
        f"Trip to {trip.destination_city}, {trip.destination_country} for {duration} days",
        f"Overall Risk Level: {risk_level} (Score: {risk_score}/100)"
    ]
    
    if risk_level == "Low":
        summary_parts.append(
            "This destination presents minimal travel risks. Standard travel precautions recommended."
        )
    elif risk_level == "Medium":
        summary_parts.append(
            "This destination presents moderate travel risks that require attention. "
            f"Key concerns: {', '.join(top_risks[:2])}. Review recommendations carefully."
        )
    else:  # High
        summary_parts.append(
            "This destination presents significant travel risks. "
            f"Key concerns: {', '.join(top_risks[:3])}. "
            "Strongly recommend consulting travel health professionals before departure."
        )
    
    if traveler.health_conditions:
        summary_parts.append(
            f"Note: Traveler has reported health conditions ({traveler.health_conditions}). "
            "Consider impact on destination environment."
        )
    
    return " ".join(summary_parts)
