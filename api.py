import requests
import streamlit as st

API_KEY = st.secrets["OPENWEATHER_API_KEY"]

def get_air_quality(city):
    """Fetch AQI + pollutant data for a given city."""
    try:
        geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo_res = requests.get(geo_url).json()

        if not geo_res or not isinstance(geo_res, list):
            return {"error": f"City '{city}' not found."}

        lat = geo_res[0]["lat"]
        lon = geo_res[0]["lon"]

        air_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        air_res = requests.get(air_url).json()

        aqi = air_res["list"][0]["main"]["aqi"]
        components = air_res["list"][0]["components"]

        return {
            "city": city,
            "aqi": aqi,
            "co": components["co"],
            "no2": components["no2"],
            "o3": components["o3"],
            "so2": components["so2"],
            "pm2_5": components["pm2_5"],
            "pm10": components["pm10"],
            "nh3": components["nh3"]
        }

    except Exception as e:
        return {"error": str(e)}