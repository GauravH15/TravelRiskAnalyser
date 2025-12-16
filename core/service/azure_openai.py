import os
from openai import AzureOpenAI
from azure.identity import ClientSecretCredential
from django.conf import settings
import json
import time
from django.conf import settings
from azure.ai.projects import AIProjectClient


RISK_ANALYSIS_INSTRUCTIONS = """
You are an enterprise business travel risk, compliance, and duty-of-care expert.

Analyze the provided business trip and return ONLY valid JSON.

The response MUST strictly follow this schema:

{
  "overall_risk_score": number (0-100),
  "risk_level": "Low" | "Medium" | "High",

  "political_and_war_risk": {
    "level": "Low" | "Medium" | "High",
    "summary": string
  },

  "labour_law_and_immigration": {
    "risk_level": "Low" | "Medium" | "High",
    "notes": string
  },

  "health_and_safety": {
    "risk_level": "Low" | "Medium" | "High",
    "notes": string
  },

  "key_risk_factors": string,
  "recommendations": string
}

Do not include any explanation outside the JSON.
"""
def _get_project_client():
    credential = ClientSecretCredential(
        tenant_id=settings.AZURE_TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET,
    )



    return AIProjectClient(
        credential=credential,
        endpoint=settings.AZURE_OPENAI_ENDPOINT
    )


def analyze_trip_risk(trip, traveler):
    """
    Analyze trip risk using Azure AI Foundry.
    Returns structured JSON.
    Does NOT store anything in DB.
    """

    project = _get_project_client()

    # 1️⃣ Create agent
    agent = project.agents.create_agent(
        model=settings.AZURE_OPENAI_MODEL,  # gpt-4o-mini
        name="Trip-Risk-Analyzer",
        instructions=RISK_ANALYSIS_INSTRUCTIONS,
    )

    # 2️⃣ Create thread
    thread = project.agents.threads.create()

    # 3️⃣ Build payload
    payload = {
        "traveler": {
            "nationality": traveler.user.nationality,
            "gender": traveler.user.gender,
            "health_conditions": traveler.health_conditions,
            "frequent_traveler": traveler.frequent_traveler,
        },
        "trip": {
            "destination_country": trip.destination_country,
            "destination_city": trip.destination_city,
            "start_date": str(trip.start_date),
            "end_date": str(trip.end_date),
            "purpose": trip.purpose,
            "transport_mode": trip.transport_mode,
            "accommodation": trip.accommodation,
            "duration_days": (trip.end_date - trip.start_date).days,
        }
    }

    # 4️⃣ Send user message
    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=json.dumps(payload),
    )

    # 5️⃣ Run agent
    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
    )

    # 6️⃣ Poll until completion
    while True:
        response = project.agents.runs.get(
            thread_id=thread.id,
            run_id=run.id,
        )

        if response.status in ("completed", "failed"):
            break

        time.sleep(0.5)

    if response.status != "completed":
        raise RuntimeError("Azure AI Foundry risk analysis failed")

    # 7️⃣ Fetch assistant response
    messages = list(project.agents.messages.list(thread_id=thread.id))
    
    for msg in reversed(messages):
        if msg.role == "assistant":
            try:
                raw_data = msg.content[0].text.value
                # Parse the JSON string, removing escape characters
                parsed_data = json.loads(raw_data)
                return parsed_data
            except Exception as e:
                print(f"Failed to convert msg into json format: {e}")
                return msg.content[0].text.value
         

    raise RuntimeError("No AI response received")
