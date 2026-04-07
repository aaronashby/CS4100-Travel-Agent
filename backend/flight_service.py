import os
import requests
from dotenv import load_dotenv

load_dotenv()

AVIATION_KEY = os.getenv("aviation_key", "")
AVIATION_BASE = "http://api.aviationstack.com/v1"

# Map common city names to their primary IATA airport codes
CITY_TO_IATA = {
    "new york": "JFK", "los angeles": "LAX", "chicago": "ORD",
    "houston": "IAH", "phoenix": "PHX", "philadelphia": "PHL",
    "san antonio": "SAT", "san diego": "SAN", "dallas": "DFW",
    "san francisco": "SFO", "austin": "AUS", "seattle": "SEA",
    "denver": "DEN", "boston": "BOS", "nashville": "BNA",
    "washington": "IAD", "miami": "MIA", "atlanta": "ATL",
    "las vegas": "LAS", "portland": "PDX", "detroit": "DTW",
    "minneapolis": "MSP", "tampa": "TPA", "orlando": "MCO",
    "toronto": "YYZ", "london": "LHR", "paris": "CDG",
    "tokyo": "NRT", "berlin": "BER", "rome": "FCO",
    "madrid": "MAD", "barcelona": "BCN", "amsterdam": "AMS",
    "dubai": "DXB", "singapore": "SIN", "hong kong": "HKG",
    "sydney": "SYD", "mumbai": "BOM", "delhi": "DEL",
    "bangkok": "BKK", "istanbul": "IST", "cairo": "CAI",
    "mexico city": "MEX", "sao paulo": "GRU", "buenos aires": "EZE",
    "johannesburg": "JNB", "nairobi": "NBO", "moscow": "SVO",
    "beijing": "PEK", "shanghai": "PVG", "seoul": "ICN",
    "osaka": "KIX", "lagos": "LOS", "lisbon": "LIS",
    "prague": "PRG", "vienna": "VIE", "zurich": "ZRH",
    "dublin": "DUB", "brussels": "BRU", "stockholm": "ARN",
    "copenhagen": "CPH", "oslo": "OSL", "helsinki": "HEL",
    "warsaw": "WAW", "budapest": "BUD", "athens": "ATH",
    "havana": "HAV", "lima": "LIM", "bogota": "BOG",
    "santiago": "SCL", "honolulu": "HNL", "anchorage": "ANC",
}


def city_to_iata(city_name):
    """Convert a city name to an IATA airport code."""
    city_lower = city_name.lower().strip()
    # Direct match
    if city_lower in CITY_TO_IATA:
        return CITY_TO_IATA[city_lower]
    # Partial match (e.g. "Boston, MA" -> "boston")
    for key, code in CITY_TO_IATA.items():
        if key in city_lower or city_lower in key:
            return code
    # Fallback: first 3 characters uppercase
    return city_name[:3].upper()


def fetch_flights(destination, start_date, end_date):
    """
    Fetch real flight data from Aviationstack API.
    Returns outbound and return flight dicts.
    """
    dest_iata = city_to_iata(destination)
    
    if not AVIATION_KEY:
        print("[Flights] No API key found, using defaults.")
        return _default_flights(destination, dest_iata, start_date, end_date)

    outbound = _fetch_one_flight(dest_iata, "arr", start_date)
    return_flight = _fetch_one_flight(dest_iata, "dep", end_date)
    
    outbound_result = _format_flight(outbound, dest_iata, start_date, direction="outbound") if outbound else None
    return_result = _format_flight(return_flight, dest_iata, end_date, direction="return") if return_flight else None

    # Fallback if API doesn't return usable data
    if not outbound_result:
        outbound_result = _default_flights(destination, dest_iata, start_date, end_date)["outbound"]
    if not return_result:
        return_result = _default_flights(destination, dest_iata, start_date, end_date)["return"]

    return {"outbound": outbound_result, "return": return_result}


def _fetch_one_flight(iata, direction, date):
    """Fetch a single flight from the API."""
    try:
        params = {
            "access_key": AVIATION_KEY,
            f"{'arr' if direction == 'arr' else 'dep'}_iata": iata,
            "flight_status": "scheduled",
            "limit": 5,
        }
        resp = requests.get(f"{AVIATION_BASE}/flights", params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            flights = data.get("data", [])
            # Pick first flight with a real airline name
            for f in flights:
                airline = f.get("airline", {}).get("name", "")
                if airline and airline.lower() not in ("empty", "none", ""):
                    return f
            # If all have empty names, return first one with any data
            if flights:
                return flights[0]
        return None
    except Exception as e:
        print(f"[Flights] API error: {e}")
        return None


def _format_flight(flight_data, dest_iata, date, direction):
    """Format raw Aviationstack data into our response structure."""
    try:
        airline_name = flight_data.get("airline", {}).get("name", "Unknown Airlines")
        if not airline_name or airline_name.lower() == "empty":
            airline_name = "Regional Airways"
            
        flight_iata = flight_data.get("flight", {}).get("iata", "")
        if not flight_iata:
            flight_iata = f"RA{flight_data.get('flight', {}).get('number', '100')}"

        dep = flight_data.get("departure", {})
        arr = flight_data.get("arrival", {})
        
        dep_time = dep.get("scheduled", f"{date}T08:00:00")
        arr_time = arr.get("scheduled", f"{date}T12:00:00")
        dep_iata = dep.get("iata", "---")
        arr_iata = arr.get("iata", dest_iata)

        return {
            "airline": airline_name,
            "flightNumber": flight_iata,
            "departureAirport": dep_iata if direction == "outbound" else arr_iata,
            "departureTime": dep_time,
            "arrivalAirport": arr_iata if direction == "outbound" else dep_iata,
            "arrivalTime": arr_time,
            "cost": 450,  # Aviationstack free tier doesn't include pricing
        }
    except Exception:
        return None


def _default_flights(destination, dest_iata, start_date, end_date):
    """Fallback flight data if API fails."""
    return {
        "outbound": {
            "airline": "Global Airways", "flightNumber": "GA100",
            "departureAirport": "Home", "departureTime": f"{start_date}T08:00:00",
            "arrivalAirport": dest_iata, "arrivalTime": f"{start_date}T10:30:00",
            "cost": 450
        },
        "return": {
            "airline": "Global Airways", "flightNumber": "GA101",
            "departureAirport": dest_iata, "departureTime": f"{end_date}T10:00:00",
            "arrivalAirport": "Home", "arrivalTime": f"{end_date}T12:30:00",
            "cost": 450
        }
    }


if __name__ == "__main__":
    flights = fetch_flights("Boston", "2026-04-10", "2026-04-12")
    import json
    print(json.dumps(flights, indent=2))
