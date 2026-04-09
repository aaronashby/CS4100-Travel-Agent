from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

# Import our AI components
from location import LocationSearcher
from poi_service import fetch_city_pois
from csp import ItineraryCSP
from astar import AStarPathfinder
from city_graph import CityGraph
from flight_service import fetch_flights
from weather_service import fetch_weather

app = Flask(__name__)
# Enabling CORS so the React frontend can make requests to this backend
CORS(app)

city_graph = CityGraph()
pathfinder = AStarPathfinder()

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from the Flask backend!"})

@app.route('/api/cities/search', methods=['GET'])
def search_cities():
    q = request.args.get('q', '').strip().lower()
    if len(q) < 2:
        return jsonify([])
    name_prefix = []
    name_contains = []
    region_matches = []
    for city in city_graph.data:
        name = city.get('name', '')
        country = city.get('country', '')
        admin_name = city.get('admin_name', '') or ''
        score = city.get('tourism_score', 0) or 0
        entry = {"name": name, "country": country, "admin_name": admin_name, "_score": score}
        name_lower = name.lower()
        admin_lower = admin_name.lower()
        country_lower = country.lower()
        if name_lower.startswith(q):
            name_prefix.append(entry)
        elif q in name_lower:
            name_contains.append(entry)
        elif admin_lower.startswith(q) or q in admin_lower or country_lower.startswith(q) or q in country_lower:
            region_matches.append(entry)
    # sorts state/country matches by tourism_score so the most popular cities 
    # appear first when searching broadly (e.g. "california" or "united states")
    region_matches.sort(key=lambda x: x["_score"], reverse=True)
    results = (name_prefix + name_contains + region_matches)[:8]
    for r in results:
        del r["_score"]  # strip internal ranking field before sending to frontend
    return jsonify(results)

@app.route('/api/plan', methods=['POST'])
def plan_trip():
    data = request.json
    destination_str = data.get('destination', '').strip()
    start_date = data.get('startDate', '')
    end_date = data.get('endDate', '')
    budget = data.get('budget', '')
    travelers = data.get('travelers', '')
    activities = data.get('activities', [])
    
    # 1. Location Selection (First Choice Hill Climbing)
    if not destination_str:
        searcher = LocationSearcher(activities)
        best_city = searcher.search()
        if best_city:
            destination_str = best_city["name"]
            city_data = best_city
        else:
            return jsonify({"error": "No suitable destination found."}), 400
    else:
        # Match provided destination string to our data
        city_data = city_graph.get_city(destination_str)
        if not city_data:
            # Geocode fallback
            try:
                gc_resp = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": destination_str, "format": "json", "limit": 1},
                    headers={"User-Agent": "CS4100-Travel-Agent/1.0"},
                    timeout=5
                )
                if gc_resp.status_code == 200 and gc_resp.json():
                    gc_data = gc_resp.json()[0]
                    city_data = {
                        "name": destination_str,
                        "latitude": float(gc_data["lat"]),
                        "longitude": float(gc_data["lon"])
                    }
            except Exception:
                pass
            if not city_data:
                city_data = {"name": destination_str, "latitude": 48.8566, "longitude": 2.3522} 

    # Calculate trip duration
    try:
        d1 = datetime.strptime(start_date, "%Y-%m-%d")
        d2 = datetime.strptime(end_date, "%Y-%m-%d")
        days = (d2 - d1).days + 1
        if days <= 0: days = 1
    except:
        days = 3

    lat = city_data.get("latitude")
    lon = city_data.get("longitude")

    # Fetch Real Flights (Aviationstack API)
    flights = fetch_flights(destination_str, start_date, end_date)

    # Fetch Weather Forecast
    weather_forecast = fetch_weather(lat, lon, days)
    # Build a date->condition map for the CSP
    weather_map = {}
    for w in weather_forecast:
        weather_map[w["date"]] = w["condition"]

    # Fetch Real POIs (Overpass API)
    pois = fetch_city_pois(lat, lon, activities)

    # Schedule Itinerary (CSP)
    csp = ItineraryCSP(days, pois, activities)
    itinerary_plan = csp.solve(start_date)

    # Inject real weather into the itinerary
    if itinerary_plan:
        for day in itinerary_plan:
            day_date = day.get("date", "")
            if day_date in weather_map:
                day["weather"] = weather_map[day_date]

    # Refine with A* (Pathfinding/Distances)
    total_distance = 0
    if itinerary_plan:
        for day in itinerary_plan:
            all_acts = day["morning"]["activities"] + day["afternoon"]["activities"] + day["evening"]["activities"]
            for i in range(len(all_acts) - 1):
                p1 = (all_acts[i]["lat"], all_acts[i]["lng"])
                p2 = (all_acts[i+1]["lat"], all_acts[i+1]["lng"])
                _, dist = pathfinder.find_path(p1, p2)
                total_distance += dist

    # Generate Packing List (weather-aware + activity-aware)
    packing_items = ["Passport", "Tickets", "Money", "Phone Charger", "Toiletries"]
    act_lower = [a.lower() for a in activities]
    
    # Activity-based items
    if "outdoors" in act_lower: 
        packing_items.extend(["Hiking boots", "Rain jacket", "Sunscreen"])
    if "museums" in act_lower: 
        packing_items.append("Walking shoes")
    if "food & drink" in act_lower: 
        packing_items.append("Dress clothes")
    if "nightlife" in act_lower: 
        packing_items.append("Party outfit")
    if "relaxation" in act_lower: 
        packing_items.extend(["Swimwear", "Beach towel"])
    if "shopping" in act_lower: 
        packing_items.append("Extra bag for gifts")
    
    # Weather-based items
    weather_conditions = [w.get("condition", "") for w in weather_forecast]
    if any(c == "rainy" for c in weather_conditions):
        packing_items.extend(["Umbrella", "Waterproof jacket"])
    if any(w.get("temp_f", 70) < 50 for w in weather_forecast):
        packing_items.append("Warm layers")
    if any(w.get("temp_f", 70) > 80 for w in weather_forecast):
        packing_items.extend(["Sunglasses", "Light clothing"])
    
    if days >= 5:
        packing_items.append("Laundry bag")
    
    num_travelers = int(travelers) if travelers else 1
    packing_items.append(f"{min(days * 2, 10)} t-shirts")
    packing_items.append(f"{min(days, 5)} pants/shorts")

    return jsonify({
        "destination": destination_str,
        "flights": flights,
        "packingList": { "items": list(set(packing_items)) },
        "itinerary": itinerary_plan or [],
        "ratings": [
            {"category": "Food & Drink", "stars": 4},
            {"category": "Outdoors", "stars": 5 if "outdoors" in act_lower else 3},
            {"category": "Museums", "stars": 4 if "museums" in act_lower else 3},
            {"category": "Nightlife", "stars": 4 if "nightlife" in act_lower else 3},
            {"category": "Local Search", "stars": 5}
        ],
        "meta": {
            "total_travel_distance_km": round(total_distance, 2),
            "algorithm": "First-Choice Hill Climbing + CSP + A*",
            "weather_source": "API" if any(w.get("description", "").startswith("Estimated") == False for w in weather_forecast) else "Heuristic"
        }
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)
