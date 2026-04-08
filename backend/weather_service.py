import os
import random
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

WEATHER_KEY = os.getenv("weather_api", "")


def _classify_weather(description):
    # Classify weather into standard types
    desc = description.lower()
    if "rain" in desc or "shower" in desc or "drizzle" in desc:
        return "rainy"
    elif "cloud" in desc or "overcast" in desc:
        if "partly" in desc or "few" in desc or "scattered" in desc:
            return "partly-cloudy"
        return "cloudy"
    elif "sun" in desc or "clear" in desc:
        return "sunny"
    elif "snow" in desc:
        return "rainy"
    else:
        return "partly-cloudy"


def _try_openweathermap(lat, lon, num_days):
    # Try OpenWeatherMap API
    try:
        params = {
            "lat": lat, "lon": lon,
            "appid": WEATHER_KEY,
            "units": "imperial",
            "cnt": 40
        }
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params=params, timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            forecasts = []
            seen_dates = set()
            for item in data.get("list", []):
                date = item["dt_txt"][:10]
                if date not in seen_dates:
                    seen_dates.add(date)
                    weather = item["weather"][0]["main"].lower()
                    temp = item["main"]["temp"]
                    condition = _classify_weather(weather)
                    forecasts.append({
                        "date": date,
                        "condition": condition,
                        "temp_f": round(temp),
                        "description": item["weather"][0]["description"]
                    })
                    if len(forecasts) >= num_days:
                        break
            if forecasts:
                return forecasts
    except Exception:
        pass
    return None


def _try_weatherapi(lat, lon, num_days):
    # Try WeatherAPI.com
    try:
        params = {
            "key": WEATHER_KEY,
            "q": f"{lat},{lon}",
            "days": min(num_days, 14)
        }
        resp = requests.get(
            "http://api.weatherapi.com/v1/forecast.json",
            params=params, timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            forecasts = []
            for day in data.get("forecast", {}).get("forecastday", [])[:num_days]:
                condition_text = day["day"]["condition"]["text"].lower()
                condition = _classify_weather(condition_text)
                forecasts.append({
                    "date": day["date"],
                    "condition": condition,
                    "temp_f": round(day["day"]["avgtemp_f"]),
                    "description": day["day"]["condition"]["text"]
                })
            if forecasts:
                return forecasts
    except Exception:
        pass
    return None


def _estimated_weather(lat, num_days):
    # Heuristic weather based on latitude
    abs_lat = abs(lat)
    today = datetime.now()

    forecasts = []
    for i in range(num_days):
        date = (today + timedelta(days=i)).strftime("%Y-%m-%d")

        if abs_lat < 23:  # Tropical
            conditions = ["sunny", "sunny", "sunny", "partly-cloudy", "rainy"]
            temp_base = 85
        elif abs_lat < 40:  # Subtropical
            conditions = ["sunny", "sunny", "partly-cloudy", "partly-cloudy", "cloudy"]
            temp_base = 72
        elif abs_lat < 55:  # Temperate
            conditions = ["partly-cloudy", "cloudy", "sunny", "rainy", "partly-cloudy"]
            temp_base = 58
        else:  # Sub-arctic
            conditions = ["cloudy", "cloudy", "rainy", "partly-cloudy", "rainy"]
            temp_base = 42

        condition = random.choice(conditions)
        temp = temp_base + random.randint(-8, 8)

        forecasts.append({
            "date": date,
            "condition": condition,
            "temp_f": temp,
            "description": f"Estimated: {condition}, {temp}°F"
        })

    return forecasts


def fetch_weather(lat, lon, num_days=7):
    # Return weather data using APIs or heuristics
    if WEATHER_KEY:
        result = _try_openweathermap(lat, lon, num_days)
        if result:
            return result

        result = _try_weatherapi(lat, lon, num_days)
        if result:
            return result

    return _estimated_weather(lat, num_days)


if __name__ == "__main__":
    import json
    weather = fetch_weather(42.3601, -71.0589, 5)  # Boston
    print(json.dumps(weather, indent=2))
