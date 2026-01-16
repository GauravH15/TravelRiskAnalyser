"""
LLM-based recommendation generator
Uses Azure OpenAI to generate intelligent health recommendations based on risk data
"""

import json
import logging
import time
from azure.identity import ClientSecretCredential
from django.conf import settings
from azure.ai.projects import AIProjectClient

logger = logging.getLogger(__name__)


HEALTH_RECOMMENDATION_INSTRUCTIONS = """
You are a travel health and disease risk expert. Based on the health and disease risk analysis data provided, 
generate practical, actionable health and safety recommendations for the traveler.

The recommendations should be:
1. Specific to the destination and disease risks
2. Prioritized by importance (most critical first)
3. Practical and actionable
4. Tailored to the traveler's health conditions if provided
5. Include vaccination, medication, prevention, and precaution advice

Return a JSON object with:
{
  "critical_recommendations": ["recommendation 1", "recommendation 2", ...],
  "health_precautions": ["precaution 1", "precaution 2", ...],
  "vaccination_advice": ["vaccine 1 advice", "vaccine 2 advice", ...],
  "daily_practices": ["practice 1", "practice 2", ...],
  "emergency_preparedness": ["item 1", "item 2", ...]
}

Provide only valid JSON, no other text.
"""


def _get_project_client():
    """Get Azure AI Project client"""
    credential = ClientSecretCredential(
        tenant_id=settings.AZURE_TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET,
    )
    
    return AIProjectClient(
        credential=credential,
        endpoint=settings.AZURE_OPENAI_ENDPOINT
    )


def generate_health_recommendations_llm(health_risk_data: dict) -> dict:
    """
    Use LLM to generate intelligent health recommendations based on disease/health risk data
    
    Args:
        health_risk_data: Dict containing COVID status, diseases, vaccines, healthcare info
        
    Returns:
        dict: Structured recommendations from LLM
    """
    
    try:
        project = _get_project_client()
        
        # Create agent
        agent = project.agents.create_agent(
            model=settings.AZURE_OPENAI_MODEL,
            name="Health-Recommendation-Agent",
            instructions=HEALTH_RECOMMENDATION_INSTRUCTIONS,
        )
        
        # Create thread
        thread = project.agents.threads.create()
        
        # Build the prompt with health data
        prompt = f"""
Destination: {health_risk_data.get('destination', 'Unknown')}
Traveler Health Conditions: {health_risk_data.get('health_conditions', 'None reported')}
Frequent Traveler: {health_risk_data.get('frequent_traveler', False)}

COVID-19 Status:
{json.dumps(health_risk_data.get('covid_data', {}), indent=2)}

Endemic Diseases:
{json.dumps(health_risk_data.get('disease_outbreaks', {}), indent=2)}

Vaccination Requirements:
- Required: {', '.join(health_risk_data.get('required_vaccines', []))}
- Recommended: {', '.join(health_risk_data.get('recommended_vaccines', []))}

Healthcare Quality: {health_risk_data.get('healthcare_quality', 'Unknown')}

Please generate comprehensive health and safety recommendations for this traveler.
"""
        
        # Send message to agent
        project.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )
        
        # Run agent
        run = project.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
        )
        
        # Poll until completion
        while True:
            response = project.agents.runs.get(
                thread_id=thread.id,
                run_id=run.id,
            )
            
            if response.status in ("completed", "failed"):
                break
            
            time.sleep(0.5)
        
        if response.status != "completed":
            logger.error("LLM recommendation generation failed")
            return None
        
        # Extract response
        messages = list(project.agents.messages.list(thread_id=thread.id))
        
        for msg in reversed(messages):
            if msg.role == "assistant":
                try:
                    raw_data = msg.content[0].text.value
                    recommendations = json.loads(raw_data)
                    return recommendations
                except Exception as e:
                    logger.error(f"Failed to parse LLM recommendations: {e}")
                    return None
        
        return None
        
    except Exception as e:
        logger.error(f"Error generating LLM recommendations: {e}")
        return None


def flatten_recommendations(llm_recommendations: dict) -> list:
    """
    Flatten LLM recommendations into a simple list
    
    Args:
        llm_recommendations: Dict from LLM with categorized recommendations
        
    Returns:
        list: Flattened list of all recommendations
    """
    
    if not llm_recommendations:
        return []
    
    recommendations = []
    
    # Add in priority order
    if llm_recommendations.get("critical_recommendations"):
        recommendations.extend(llm_recommendations["critical_recommendations"])
    
    if llm_recommendations.get("vaccination_advice"):
        recommendations.extend(llm_recommendations["vaccination_advice"])
    
    if llm_recommendations.get("health_precautions"):
        recommendations.extend(llm_recommendations["health_precautions"])
    
    if llm_recommendations.get("daily_practices"):
        recommendations.extend(llm_recommendations["daily_practices"])
    
    if llm_recommendations.get("emergency_preparedness"):
        recommendations.extend(llm_recommendations["emergency_preparedness"])
    
    return recommendations
