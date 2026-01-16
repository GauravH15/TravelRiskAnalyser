"""
Geocoding tools to convert city names to coordinates
Uses free APIs with no rate limits
"""

import requests
import logging

logger = logging.getLogger(__name__)


def get_coordinates(city: str, country: str) -> tuple:
    """
    Get latitude and longitude for a city using Open-Meteo Geocoding API (FREE, no key needed)
    
    Args:
        city: City name
        country: Country name
        
    Returns:
        tuple: (latitude, longitude) or (None, None) if not found
    """
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city,
            "country": country,
            "language": "en",
            "limit": 1
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            return (result["latitude"], result["longitude"])
        else:
            logger.warning(f"Could not find coordinates for {city}, {country}")
            return (None, None)
            
    except Exception as e:
        logger.error(f"Error fetching coordinates: {e}")
        return (None, None)


def get_country_code(country: str) -> str:
    """
    Get ISO country code for a country name using REST Countries API (FREE)
    
    Args:
        country: Country name
        
    Returns:
        str: ISO 3166-1 alpha-3 country code (e.g., "USA", "GBR")
    """
    try:
        url = f"https://restcountries.com/v3.1/name/{country}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0].get("cca3", "").upper()
        
        return country.upper()[:3]
        
    except Exception as e:
        logger.error(f"Error fetching country code: {e}")
        return country.upper()[:3]
